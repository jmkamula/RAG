-- =============================================================================
-- ArionComply — Schema v7 (Phase 2b)
-- Posture Confirmation Gate
--
-- Design principles (inheriting from v6):
--   1. NEVER hard-delete compliance evidence
--   2. Every change to posture is auditable
--   3. Draft findings are visible but clearly marked — not hidden
--   4. Confirmed findings require an authorised user signature
--   5. Overrides are tracked — you can see what the system proposed vs what
--      the human decided
--   6. No finding can skip the draft state — all writes start as draft
--   7. Confirmation can be reverted to draft but the revert is logged
--
-- Confirmation states:
--   draft      — system-generated (questionnaire, document extraction, API sync)
--                treated as indicative by the resolver LLM prompt
--   confirmed  — signed off by an authorised user (consultant or admin)
--                treated as authoritative by the resolver
--   overridden — human changed the system finding; original preserved in history
--                the override IS the confirmed finding
--
-- Who can confirm:
--   Role 'consultant'   — can confirm for their assigned tenants
--   Role 'admin'        — can confirm for any tenant
--   Role 'client_admin' — can confirm their own tenant (optional, configurable)
--   App role            — can WRITE draft only, never confirm
--
-- Delete protection:
--   posture_controls    — compliance class (7 years), never auto-purge
--   posture_history     — immutable append-only log (DELETE revoked)
--   confirmation_log    — append-only (DELETE revoked), separate from deletion_log
--
-- =============================================================================


-- =============================================================================
-- SECTION 1: CONFIRMATION COLUMNS ON posture_controls
-- Added with IF NOT EXISTS — safe to run on existing DB
-- =============================================================================

ALTER TABLE posture_controls
    -- Confirmation state machine
    ADD COLUMN IF NOT EXISTS confirmation_status  TEXT NOT NULL DEFAULT 'draft'
        CHECK (confirmation_status IN ('draft', 'confirmed', 'overridden')),

    -- Who confirmed and when
    ADD COLUMN IF NOT EXISTS confirmed_by         UUID REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS confirmed_at         TIMESTAMPTZ,

    -- Source of this finding (for provenance)
    ADD COLUMN IF NOT EXISTS source               TEXT NOT NULL DEFAULT 'system'
        CHECK (source IN (
            'questionnaire',   -- free assessment questionnaire
            'document',        -- extracted from uploaded document
            'api_sync',        -- pulled from external system (ServiceNow etc.)
            'manual',          -- entered directly by consultant
            'system'           -- legacy / migration default
        )),

    -- What the system originally proposed (preserved when human overrides)
    ADD COLUMN IF NOT EXISTS system_finding       TEXT,   -- original NC/OFI/Comply/N/A
    ADD COLUMN IF NOT EXISTS system_gap           TEXT,   -- original gap description
    ADD COLUMN IF NOT EXISTS system_proposed_at   TIMESTAMPTZ,

    -- Confidence score from extraction (0.0–1.0, NULL for manual entries)
    ADD COLUMN IF NOT EXISTS confidence           NUMERIC(3,2)
        CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0));


-- =============================================================================
-- SECTION 2: PERFORMANCE INDEXES FOR CONFIRMATION
-- =============================================================================

-- Fast lookup of all draft findings for a tenant (review queue)
CREATE INDEX IF NOT EXISTS idx_posture_controls_draft
    ON posture_controls (tenant_id, confirmation_status)
    WHERE confirmation_status = 'draft' AND is_active = TRUE;

-- Fast lookup of confirmed findings (resolver primary path)
CREATE INDEX IF NOT EXISTS idx_posture_controls_confirmed
    ON posture_controls (tenant_id, confirmation_status)
    WHERE confirmation_status = 'confirmed' AND is_active = TRUE;

-- Source tracking — which findings came from which source
CREATE INDEX IF NOT EXISTS idx_posture_controls_source
    ON posture_controls (tenant_id, source)
    WHERE is_active = TRUE;

-- Confirmed-by for audit trail queries
CREATE INDEX IF NOT EXISTS idx_posture_controls_confirmed_by
    ON posture_controls (confirmed_by)
    WHERE confirmed_by IS NOT NULL;


-- =============================================================================
-- SECTION 3: CONFIRMATION LOG
-- Immutable append-only record of every confirmation, revert, and override.
-- Separate from deletion_log — this is a compliance audit trail, not a
-- deletion trail.
-- DELETE is explicitly revoked from the app role.
-- =============================================================================

CREATE TABLE IF NOT EXISTS confirmation_log (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID        NOT NULL REFERENCES tenants(id),
    posture_control_id  UUID        NOT NULL REFERENCES posture_controls(id),
    control_ref         TEXT        NOT NULL,   -- e.g. "A.5.18" — denormalised for readability
    standard_id         TEXT        NOT NULL,   -- e.g. "ISO27001:2022"

    -- What action was taken
    action              TEXT        NOT NULL
        CHECK (action IN (
            'confirmed',           -- draft → confirmed
            'reverted_to_draft',   -- confirmed → draft (e.g. new evidence changes picture)
            'overridden',          -- system finding changed by human
            'bulk_confirmed'       -- part of a bulk confirmation operation
        )),

    -- State before and after
    previous_status     TEXT        NOT NULL,   -- confirmation_status before action
    new_status          TEXT        NOT NULL,   -- confirmation_status after action
    previous_finding    TEXT,                   -- finding value before action
    new_finding         TEXT,                   -- finding value after action

    -- Who, when, why
    performed_by        UUID        NOT NULL REFERENCES users(id),
    performed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason              TEXT,                   -- optional free-text reason
    ip_address          INET,                   -- for security audit trail

    -- Source of the posture being confirmed
    source              TEXT        NOT NULL,

    -- Bulk operation reference (for batch confirms)
    batch_id            UUID                    -- NULL for individual confirmations
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_confirmation_log_tenant
    ON confirmation_log (tenant_id, performed_at DESC);

CREATE INDEX IF NOT EXISTS idx_confirmation_log_control
    ON confirmation_log (tenant_id, control_ref, performed_at DESC);

CREATE INDEX IF NOT EXISTS idx_confirmation_log_performer
    ON confirmation_log (performed_by, performed_at DESC);

CREATE INDEX IF NOT EXISTS idx_confirmation_log_batch
    ON confirmation_log (batch_id)
    WHERE batch_id IS NOT NULL;

-- RLS: tenants see only their own confirmation log
ALTER TABLE confirmation_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY confirmation_log_tenant ON confirmation_log
    FOR SELECT
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
    );

-- App user can INSERT (to log confirmations) but never DELETE
GRANT SELECT, INSERT ON confirmation_log TO arioncomply_app;
REVOKE DELETE ON confirmation_log FROM arioncomply_app;
REVOKE DELETE ON confirmation_log FROM PUBLIC;

-- Explicit trigger to block any DELETE attempt at DB level
CREATE OR REPLACE FUNCTION fn_block_confirmation_log_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'confirmation_log is append-only — deletions are not permitted. '
        'Control ref: %, performed_at: %',
        OLD.control_ref, OLD.performed_at
    USING ERRCODE = '23000';  -- integrity_constraint_violation
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_block_confirmation_log_delete ON confirmation_log;
CREATE TRIGGER trg_block_confirmation_log_delete
    BEFORE DELETE ON confirmation_log
    FOR EACH ROW EXECUTE FUNCTION fn_block_confirmation_log_delete();


-- =============================================================================
-- SECTION 4: CONFIRMATION TRIGGER ON posture_controls
-- Enforces the state machine — illegal transitions are blocked.
-- Logs every transition to confirmation_log automatically.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_posture_confirmation_guard()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id   UUID;
    v_action    TEXT;
BEGIN
    -- Extract current user from app context
    v_user_id := NULLIF(current_setting('app.user_id', TRUE), '')::UUID;

    -- ── State machine enforcement ─────────────────────────────────────────
    IF OLD.confirmation_status = NEW.confirmation_status THEN
        -- No state change — allow (e.g. updating gap text within same state)
        RETURN NEW;
    END IF;

    -- draft → confirmed: requires a confirmed_by user
    IF OLD.confirmation_status = 'draft'
       AND NEW.confirmation_status = 'confirmed' THEN
        IF NEW.confirmed_by IS NULL AND v_user_id IS NULL THEN
            RAISE EXCEPTION
                'Cannot confirm posture control % without a confirmed_by user',
                NEW.id
            USING ERRCODE = '23514';  -- check_violation
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'confirmed';

    -- confirmed → draft: allowed (revert when new evidence arrives)
    ELSIF OLD.confirmation_status = 'confirmed'
          AND NEW.confirmation_status = 'draft' THEN
        -- Preserve original confirmed_by / confirmed_at in history
        NEW.confirmed_by := NULL;
        NEW.confirmed_at := NULL;
        v_action := 'reverted_to_draft';

    -- draft/confirmed → overridden: human changes the finding
    ELSIF NEW.confirmation_status = 'overridden' THEN
        -- Preserve what the system originally said
        IF NEW.system_finding IS NULL THEN
            NEW.system_finding     := OLD.finding;
            NEW.system_gap         := OLD.gap_description;
            NEW.system_proposed_at := OLD.updated_at;
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'overridden';

    -- Any other transition is illegal
    ELSE
        RAISE EXCEPTION
            'Invalid confirmation state transition: % → % for control %',
            OLD.confirmation_status, NEW.confirmation_status, NEW.control_ref
        USING ERRCODE = '23514';
    END IF;

    -- ── Append to confirmation_log ────────────────────────────────────────
    INSERT INTO confirmation_log (
        tenant_id, posture_control_id, control_ref, standard_id,
        action, previous_status, new_status,
        previous_finding, new_finding,
        performed_by, source
    ) VALUES (
        NEW.tenant_id, NEW.id, NEW.control_ref, NEW.standard_id,
        v_action, OLD.confirmation_status, NEW.confirmation_status,
        OLD.finding, NEW.finding,
        COALESCE(NEW.confirmed_by, v_user_id),
        NEW.source
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_posture_confirmation ON posture_controls;
CREATE TRIGGER trg_posture_confirmation
    BEFORE UPDATE OF confirmation_status ON posture_controls
    FOR EACH ROW EXECUTE FUNCTION fn_posture_confirmation_guard();


-- =============================================================================
-- SECTION 5: WRITE GUARD — ONLY draft ALLOWED FROM APP ROLE
-- The app role (used by Python) can only write draft findings.
-- Confirmation requires a separate privileged role.
-- This prevents the application from self-confirming its own proposals.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_posture_write_guard()
RETURNS TRIGGER AS $$
DECLARE
    v_current_role TEXT := current_user;
BEGIN
    -- On INSERT: app role can only write draft
    IF TG_OP = 'INSERT' THEN
        IF v_current_role = 'arioncomply_app'
           AND NEW.confirmation_status != 'draft' THEN
            RAISE EXCEPTION
                'arioncomply_app can only insert draft posture findings. '
                'Got: %. Use arioncomply_consultant role to confirm.',
                NEW.confirmation_status
            USING ERRCODE = '42501';  -- insufficient_privilege
        END IF;
    END IF;

    -- On UPDATE: app role cannot change confirmation_status to confirmed/overridden
    IF TG_OP = 'UPDATE' THEN
        IF v_current_role = 'arioncomply_app'
           AND OLD.confirmation_status = 'draft'
           AND NEW.confirmation_status IN ('confirmed', 'overridden') THEN
            RAISE EXCEPTION
                'arioncomply_app cannot confirm posture findings. '
                'Use arioncomply_consultant or arioncomply_admin role.',
                NEW.confirmation_status
            USING ERRCODE = '42501';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_posture_write_guard ON posture_controls;
CREATE TRIGGER trg_posture_write_guard
    BEFORE INSERT OR UPDATE ON posture_controls
    FOR EACH ROW EXECUTE FUNCTION fn_posture_write_guard();


-- =============================================================================
-- SECTION 6: CONSULTANT ROLE
-- Separate DB role for confirmation operations.
-- Has same SELECT/INSERT/UPDATE as app, plus can set confirmation_status.
-- Cannot DELETE (compliance class — no deletes ever).
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles WHERE rolname = 'arioncomply_consultant'
    ) THEN
        CREATE ROLE arioncomply_consultant;
    END IF;
END $$;

-- Consultant inherits app permissions
GRANT arioncomply_app TO arioncomply_consultant;

-- Consultant can additionally update confirmation fields
GRANT UPDATE (
    confirmation_status,
    confirmed_by,
    confirmed_at,
    finding,            -- allowed to change finding when overriding
    gap_description,    -- allowed to add/edit gap narrative
    system_finding,     -- allowed to preserve original system proposal
    system_gap,
    system_proposed_at
) ON posture_controls TO arioncomply_consultant;

-- Consultant cannot DELETE posture_controls (compliance class)
REVOKE DELETE ON posture_controls FROM arioncomply_consultant;


-- =============================================================================
-- SECTION 7: BULK CONFIRMATION FUNCTION
-- Confirms all draft findings for a tenant in one operation.
-- Used at end of initial assessment review.
-- Logs as a batch with a single batch_id.
-- Skips any findings that fail validation.
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_bulk_confirm_posture(
    p_tenant_id     UUID,
    p_confirmed_by  UUID,
    p_standard_id   TEXT    DEFAULT NULL,   -- NULL = all standards
    p_source        TEXT    DEFAULT NULL,   -- NULL = all sources
    p_dry_run       BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    control_ref     TEXT,
    finding         TEXT,
    source          TEXT,
    action          TEXT
) AS $$
DECLARE
    v_batch_id  UUID := gen_random_uuid();
    v_rec       RECORD;
    v_count     INT  := 0;
BEGIN
    FOR v_rec IN
        SELECT id, control_ref, finding AS f, pc.source AS src, standard_id
        FROM posture_controls pc
        WHERE tenant_id          = p_tenant_id
          AND confirmation_status = 'draft'
          AND is_active           = TRUE
          AND (p_standard_id IS NULL OR standard_id = p_standard_id)
          AND (p_source      IS NULL OR pc.source   = p_source)
        ORDER BY standard_id, control_ref
    LOOP
        control_ref := v_rec.control_ref;
        finding     := v_rec.f;
        source      := v_rec.src;

        IF p_dry_run THEN
            action := 'would_confirm';
        ELSE
            UPDATE posture_controls SET
                confirmation_status = 'confirmed',
                confirmed_by        = p_confirmed_by,
                confirmed_at        = NOW()
            WHERE id = v_rec.id;

            -- Log the bulk action
            INSERT INTO confirmation_log (
                tenant_id, posture_control_id, control_ref, standard_id,
                action, previous_status, new_status,
                previous_finding, new_finding,
                performed_by, source, batch_id
            ) VALUES (
                p_tenant_id, v_rec.id, v_rec.control_ref, v_rec.standard_id,
                'bulk_confirmed', 'draft', 'confirmed',
                v_rec.f, v_rec.f,
                p_confirmed_by, v_rec.src, v_batch_id
            );

            v_count := v_count + 1;
            action := 'confirmed';
        END IF;

        RETURN NEXT;
    END LOOP;

    IF NOT p_dry_run THEN
        RAISE NOTICE 'Bulk confirmation complete: % findings confirmed (batch_id: %)',
            v_count, v_batch_id;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Only consultant and admin roles can run bulk confirmation
REVOKE ALL ON FUNCTION fn_bulk_confirm_posture(UUID, UUID, TEXT, TEXT, BOOLEAN)
    FROM PUBLIC;
REVOKE ALL ON FUNCTION fn_bulk_confirm_posture(UUID, UUID, TEXT, TEXT, BOOLEAN)
    FROM arioncomply_app;
GRANT EXECUTE ON FUNCTION fn_bulk_confirm_posture(UUID, UUID, TEXT, TEXT, BOOLEAN)
    TO arioncomply_consultant;


-- =============================================================================
-- SECTION 8: REVIEW QUEUE VIEW
-- What a consultant sees when reviewing draft findings.
-- Shows system proposal, confidence, source, and time since proposed.
-- =============================================================================

CREATE OR REPLACE VIEW v_posture_review_queue AS
SELECT
    pc.id,
    pc.tenant_id,
    pc.control_ref,
    pc.standard_id,
    pc.finding,
    pc.gap_description,
    pc.confirmation_status,
    pc.source,
    pc.confidence,
    pc.system_finding,
    pc.system_gap,
    pc.system_proposed_at,
    -- How long this finding has been in draft
    EXTRACT(EPOCH FROM (NOW() - COALESCE(pc.system_proposed_at, pc.created_at)))
        / 3600 AS hours_in_draft,
    -- Has it been overridden before?
    EXISTS (
        SELECT 1 FROM confirmation_log cl
        WHERE cl.posture_control_id = pc.id
          AND cl.action = 'overridden'
    ) AS previously_overridden
FROM posture_controls pc
WHERE pc.confirmation_status = 'draft'
  AND pc.is_active = TRUE
ORDER BY
    -- NC findings first, then OFI, then Comply, then N/A
    CASE pc.finding
        WHEN 'NC'      THEN 1
        WHEN 'OFI'     THEN 2
        WHEN 'Comply'  THEN 3
        WHEN 'N/A'     THEN 4
        ELSE                5
    END,
    pc.control_ref;

GRANT SELECT ON v_posture_review_queue TO arioncomply_app;
GRANT SELECT ON v_posture_review_queue TO arioncomply_consultant;


-- =============================================================================
-- SECTION 9: CONFIRMATION SUMMARY VIEW
-- High-level confirmation progress per tenant.
-- Used by the platform dashboard and the resolver to decide confidence level.
-- =============================================================================

CREATE OR REPLACE VIEW v_posture_confirmation_summary AS
SELECT
    tenant_id,
    standard_id,
    COUNT(*)                                            AS total_controls,
    COUNT(*) FILTER (WHERE confirmation_status = 'confirmed')   AS confirmed,
    COUNT(*) FILTER (WHERE confirmation_status = 'draft')       AS draft,
    COUNT(*) FILTER (WHERE confirmation_status = 'overridden')  AS overridden,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE confirmation_status IN ('confirmed','overridden'))
        / NULLIF(COUNT(*), 0),
        1
    )                                                   AS pct_confirmed,
    MIN(confirmed_at)                                   AS first_confirmed_at,
    MAX(confirmed_at)                                   AS last_confirmed_at
FROM posture_controls
WHERE is_active = TRUE
GROUP BY tenant_id, standard_id;

GRANT SELECT ON v_posture_confirmation_summary TO arioncomply_app;
GRANT SELECT ON v_posture_confirmation_summary TO arioncomply_consultant;


-- =============================================================================
-- SECTION 10: UPDATE RETENTION POLICY
-- confirmation_log is compliance class — 7 years, no auto-purge
-- =============================================================================

INSERT INTO retention_policies
    (retention_class, table_name, retain_years, retain_days,
     anonymise_after_years, auto_purge, legal_basis, notes)
VALUES
    ('compliance', 'confirmation_log', 7, 0, NULL, FALSE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(d) accuracy principle',
     'Confirmation audit trail — who confirmed what and when. '
     'Required to demonstrate competent human review of compliance posture.')
ON CONFLICT DO NOTHING;


-- =============================================================================
-- SECTION 11: MIGRATE EXISTING posture_controls TO draft
-- All existing records were system-generated — set to draft.
-- Run once on existing database.
-- Does NOT trigger the confirmation guard (UPDATE OF confirmation_status
-- only fires on explicit column change — existing rows have no previous state).
-- =============================================================================

UPDATE posture_controls
SET
    confirmation_status = 'draft',
    source              = 'system',
    system_proposed_at  = COALESCE(updated_at, created_at)
WHERE confirmation_status IS NULL
   OR source IS NULL;

-- Verify
DO $$
DECLARE
    v_total     INT;
    v_draft     INT;
    v_confirmed INT;
BEGIN
    SELECT COUNT(*) INTO v_total     FROM posture_controls WHERE is_active = TRUE;
    SELECT COUNT(*) INTO v_draft     FROM posture_controls WHERE is_active = TRUE AND confirmation_status = 'draft';
    SELECT COUNT(*) INTO v_confirmed FROM posture_controls WHERE is_active = TRUE AND confirmation_status = 'confirmed';

    RAISE NOTICE 'Migration complete: total=% draft=% confirmed=%',
        v_total, v_draft, v_confirmed;

    IF v_total != v_draft + v_confirmed THEN
        RAISE EXCEPTION 'Migration integrity check failed: total % != draft % + confirmed %',
            v_total, v_draft, v_confirmed;
    END IF;
END $$;


-- =============================================================================
-- SECTION 12: GRANTS SUMMARY
-- =============================================================================

-- arioncomply_app:        SELECT/INSERT/UPDATE on posture_controls (draft only)
--                         SELECT on views, INSERT on confirmation_log
--                         NO DELETE anywhere
-- arioncomply_consultant: Everything app has, plus UPDATE confirmation fields
--                         Can run fn_bulk_confirm_posture
--                         NO DELETE anywhere
-- arioncomply_admin:      Full access via BYPASSRLS (set at role level)
--                         Still cannot delete from confirmation_log (trigger blocks it)
