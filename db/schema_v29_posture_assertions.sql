-- =============================================================================
-- schema_v29_posture_assertions.sql
--
-- Phase 1a of the actor-model rework. Introduces posture_assertions — the
-- per-source truth table that lets tenant claims, assessor verdicts, and
-- engine computation coexist as parallel facts rather than collapsing into
-- one posture_controls.finding column where last-write wins.
--
-- Why now: the workbook intake conversation surfaced that posture_controls
-- conflates three different epistemics — what the tenant says, what an
-- assessor reviewed, what the evidence computes — and overwrites between
-- them. Three-actor coexistence is the foundation for the workbook
-- multi-track classifier (Phase 2), per-MUST evidence tagging (Phase 3),
-- and the assessor surface (Phase 5).
--
-- Phase 1a SCOPE (this migration):
--   * Create the table + indexes + RLS.
--   * Backfill from current posture_controls.finding (one tenant/engine/
--     assessor row per active control depending on source).
--   * Backfill pending engine proposals (engine_proposal_status='proposed')
--     as posture_assertions rows with status='pending'.
--   * Install a REVERSE-SYNC trigger that mirrors finding/gap/conf/source
--     changes on posture_controls → posture_assertions. Writers stay
--     unchanged. Engine PROPOSAL writes (engine_proposed_finding column,
--     no finding change) are intentionally NOT mirrored by the trigger
--     in 1a — they will be when posture_loader is swapped to use the
--     set_assertion() helper directly in Phase 1b. The backfill captures
--     today's pending proposals at migration time.
--
-- NOT in scope for 1a:
--   * No writer changes (posture_writer / stage1 / stage2 / posture_loader
--     / workbook_importer untouched).
--   * No reader changes (api_server / context_assembler / engine readers
--     still consume posture_controls.finding).
--   * posture_controls does NOT become a VIEW yet.
--   * No assessor surface, no chat composition rule.
--
-- Append-only with supersession: every change INSERTs a new row; the prior
-- active row gets status='superseded' + superseded_at + superseded_by_id.
-- History is `WHERE tenant_id=? AND control_ref=? ORDER BY set_at`. Partial
-- unique indexes enforce one active + one pending row per (tenant, control,
-- standard, source).
--
-- Idempotent. Self-committing per [[sql-dry-run-nested-transaction]].
-- =============================================================================

BEGIN;

-- ───────── Table ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posture_assertions (
    id                 bigserial    PRIMARY KEY,
    tenant_id          uuid         NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    control_ref        text         NOT NULL,
    standard_id        text         NOT NULL,
    source             text         NOT NULL,
    finding            text         NOT NULL,
    gap_description    text,
    confidence         text,
    set_by             text         NOT NULL,
    set_at             timestamptz  NOT NULL DEFAULT now(),
    status             text         NOT NULL DEFAULT 'active',
    superseded_at      timestamptz,
    superseded_by_id   bigint       REFERENCES posture_assertions(id) ON DELETE SET NULL,
    metadata           jsonb        NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT posture_assertions_source_check
        CHECK (source = ANY (ARRAY['tenant'::text, 'assessor'::text, 'engine'::text])),
    CONSTRAINT posture_assertions_finding_check
        CHECK (finding = ANY (ARRAY[
            'NC'::text, 'OFI'::text, 'Comply'::text, 'N/A'::text, 'Not assessed'::text
        ])),
    CONSTRAINT posture_assertions_status_check
        CHECK (status = ANY (ARRAY['active'::text, 'pending'::text, 'superseded'::text])),
    CONSTRAINT posture_assertions_superseded_consistency
        CHECK ((status = 'superseded') = (superseded_at IS NOT NULL))
);

-- ───────── Indexes ────────────────────────────────────────────────────────
-- One active assertion per (tenant, control, standard, source). Supersession
-- is the only mutator — never UPDATE finding in place.
CREATE UNIQUE INDEX IF NOT EXISTS uq_posture_assertions_active
    ON posture_assertions (tenant_id, control_ref, standard_id, source)
    WHERE status = 'active';

-- One pending assertion per (tenant, control, standard, source). Used for
-- engine proposals awaiting Stage-2 approval; tenant + assessor sources
-- never go through 'pending' in current design but the index is uniform.
CREATE UNIQUE INDEX IF NOT EXISTS uq_posture_assertions_pending
    ON posture_assertions (tenant_id, control_ref, standard_id, source)
    WHERE status = 'pending';

-- Primary lookup: "show me X's current posture across all sources".
CREATE INDEX IF NOT EXISTS idx_posture_assertions_lookup
    ON posture_assertions (tenant_id, control_ref, standard_id)
    WHERE status IN ('active', 'pending');

-- Pending queue: "show me engine proposals awaiting review".
CREATE INDEX IF NOT EXISTS idx_posture_assertions_pending_queue
    ON posture_assertions (tenant_id, source)
    WHERE status = 'pending';

-- Timeline: "how did A.5.18 evolve over time across all sources?"
CREATE INDEX IF NOT EXISTS idx_posture_assertions_history
    ON posture_assertions (tenant_id, control_ref, standard_id, source, set_at DESC);

-- ───────── RLS ────────────────────────────────────────────────────────────
-- Match posture_status_log pattern: arioncomply_app gets constant-true policy,
-- tenant scoping enforced at query layer via set_config('app.tenant_id').
-- Superuser bypasses.
ALTER TABLE posture_assertions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_posture_assertions ON posture_assertions;
CREATE POLICY app_all_posture_assertions ON posture_assertions
    FOR ALL
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE ON posture_assertions TO arioncomply_app;
GRANT USAGE, SELECT ON SEQUENCE posture_assertions_id_seq TO arioncomply_app;
-- UPDATE is required because supersession sets status='superseded' on the
-- prior row. The writer (set_assertion in rag/posture/assertions.py, Phase 1b)
-- and the reverse-sync trigger below are the only writers; both restrict
-- UPDATE to status/superseded_at/superseded_by_id fields by discipline.

-- ───────── Reverse-sync trigger ───────────────────────────────────────────
-- Phase 1a: writers continue to UPDATE posture_controls.finding directly.
-- This trigger mirrors finding/gap_description/confidence/source changes
-- into posture_assertions so the new table is kept current without touching
-- any writer. Phase 1b will swap the writers and replace this with a
-- forward-sync trigger (or drop the trigger and update posture_controls
-- via writer-side code).
--
-- Source mapping (posture_controls.source → posture_assertions.source):
--   'workbook'         → 'tenant'
--   'chat'             → 'tenant'
--   'questionnaire'    → 'tenant'
--   'document'         → 'tenant'   (doc pipeline extraction confirmed by tenant)
--   'self_reported'    → 'tenant'
--   'Not assessed'     → 'tenant'   (initial seed; tenant hasn't claimed)
--   'engine'           → 'engine'   (Stage-2 approved engine verdict)
--   'engine_backfill'  → 'engine'
--   'assessor'         → 'assessor'
--   anything else      → 'tenant'   (defensive fallback)

CREATE OR REPLACE FUNCTION fn_posture_controls_to_assertion()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    actor          text;
    prior_id       bigint;
    new_id         bigint;
BEGIN
    -- Skip noise: only fire when an actor-attributable column changes.
    IF TG_OP = 'UPDATE' THEN
        IF NEW.finding         IS NOT DISTINCT FROM OLD.finding
           AND NEW.source         IS NOT DISTINCT FROM OLD.source
           AND NEW.gap_description IS NOT DISTINCT FROM OLD.gap_description
           AND NEW.confidence     IS NOT DISTINCT FROM OLD.confidence THEN
            RETURN NEW;
        END IF;
    END IF;

    actor := CASE NEW.source
        WHEN 'workbook'        THEN 'tenant'
        WHEN 'chat'            THEN 'tenant'
        WHEN 'questionnaire'   THEN 'tenant'
        WHEN 'document'        THEN 'tenant'
        WHEN 'self_reported'   THEN 'tenant'
        WHEN 'Not assessed'    THEN 'tenant'
        WHEN 'engine'          THEN 'engine'
        WHEN 'engine_backfill' THEN 'engine'
        WHEN 'assessor'        THEN 'assessor'
        ELSE 'tenant'
    END;

    -- Supersede prior active assertion for this (tenant, control, std, actor).
    UPDATE posture_assertions
       SET status        = 'superseded',
           superseded_at = now()
     WHERE tenant_id   = NEW.tenant_id
       AND control_ref = NEW.control_ref
       AND standard_id = NEW.standard_id
       AND source      = actor
       AND status      = 'active'
     RETURNING id INTO prior_id;

    INSERT INTO posture_assertions (
        tenant_id, control_ref, standard_id, source,
        finding, gap_description, confidence,
        set_by, status, metadata
    ) VALUES (
        NEW.tenant_id, NEW.control_ref, NEW.standard_id, actor,
        NEW.finding, NEW.gap_description, NEW.confidence,
        'trigger:' || NEW.source, 'active',
        jsonb_build_object(
            'posture_controls_id',    NEW.id,
            'pc_source',              NEW.source,
            'pc_confirmation_status', NEW.confirmation_status
        )
    )
    RETURNING id INTO new_id;

    IF prior_id IS NOT NULL THEN
        UPDATE posture_assertions
           SET superseded_by_id = new_id
         WHERE id = prior_id;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_posture_controls_to_assertion ON posture_controls;
CREATE TRIGGER trg_posture_controls_to_assertion
    AFTER INSERT OR UPDATE ON posture_controls
    FOR EACH ROW
    EXECUTE FUNCTION fn_posture_controls_to_assertion();

-- ───────── Backfill ───────────────────────────────────────────────────────
-- One-time snapshot of current state. Idempotent via partial unique indexes.

-- Active assertions: one per active posture_controls row, source mapped.
INSERT INTO posture_assertions (
    tenant_id, control_ref, standard_id, source,
    finding, gap_description, confidence,
    set_by, set_at, status, metadata
)
SELECT
    tenant_id,
    control_ref,
    standard_id,
    CASE source
        WHEN 'workbook'        THEN 'tenant'
        WHEN 'chat'            THEN 'tenant'
        WHEN 'questionnaire'   THEN 'tenant'
        WHEN 'document'        THEN 'tenant'
        WHEN 'self_reported'   THEN 'tenant'
        WHEN 'Not assessed'    THEN 'tenant'
        WHEN 'engine'          THEN 'engine'
        WHEN 'engine_backfill' THEN 'engine'
        WHEN 'assessor'        THEN 'assessor'
        ELSE 'tenant'
    END AS source,
    finding,
    gap_description,
    confidence,
    'backfill:schema_v29' AS set_by,
    COALESCE(last_updated, assessed_at, now()) AS set_at,
    'active' AS status,
    jsonb_build_object(
        'posture_controls_id',    id,
        'pc_source',              source,
        'pc_confirmation_status', confirmation_status,
        'backfill',               true
    ) AS metadata
FROM posture_controls
WHERE is_active = TRUE
ON CONFLICT (tenant_id, control_ref, standard_id, source) WHERE status = 'active'
DO NOTHING;

-- Pending engine proposals: separate row, status='pending', engine source.
-- A control can have BOTH an active assertion (live finding) AND a pending
-- engine proposal (a new verdict awaiting Stage-2 approval).
INSERT INTO posture_assertions (
    tenant_id, control_ref, standard_id, source,
    finding, gap_description, confidence,
    set_by, set_at, status, metadata
)
SELECT
    tenant_id,
    control_ref,
    standard_id,
    'engine' AS source,
    engine_proposed_finding AS finding,
    engine_proposal_reason AS gap_description,
    confidence,
    'backfill:engine_proposal' AS set_by,
    COALESCE(engine_proposed_at, now()) AS set_at,
    'pending' AS status,
    jsonb_build_object(
        'posture_controls_id',      id,
        'engine_proposal_status',   engine_proposal_status,
        'live_finding_at_backfill', finding,
        'backfill',                 true
    ) AS metadata
FROM posture_controls
WHERE is_active = TRUE
  AND engine_proposal_status = 'proposed'
  AND engine_proposed_finding IS NOT NULL
ON CONFLICT (tenant_id, control_ref, standard_id, source) WHERE status = 'pending'
DO NOTHING;

COMMIT;
