-- =============================================================================
-- ArionComply — Schema v6
-- Soft Delete + Data Retention + Deletion Audit Log
--
-- Design principles:
--   1. NEVER hard-delete compliance evidence
--   2. Every deletion is auditable (deletion_log is append-only)
--   3. Retention periods are data, not code (retention_policies table)
--   4. Personal data is anonymised in-place, not deleted
--   5. RLS enforces is_active=TRUE — deleted records invisible to app
--   6. Purge job runs nightly — only touches records past purge_after date
--
-- Retention classes:
--   compliance    7 years  posture, audits, incidents, document findings
--   operational   5 years  risks, vendors, documents, remediation
--   personal_data erasure  users, contact data — anonymise on Art.17 request
--   platform      active   tenant config — soft delete on offboarding
--   session       90 days  chat history — hard delete after window
-- =============================================================================


-- =============================================================================
-- SECTION 1: RETENTION POLICY TABLE
-- Master table of retention rules per class and table
-- =============================================================================

CREATE TABLE IF NOT EXISTS retention_policies (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID REFERENCES tenants(id),  -- NULL = platform default
    retention_class       TEXT NOT NULL,
    table_name            TEXT,                          -- NULL = class-level default
    retain_years          INT  NOT NULL,                 -- 0 = no fixed period
    retain_days           INT  NOT NULL DEFAULT 0,       -- used when retain_years=0
    anonymise_after_years INT,                           -- anonymise PII before purge
    auto_purge            BOOLEAN NOT NULL DEFAULT FALSE,-- system purges automatically
    legal_basis           TEXT NOT NULL,
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, retention_class, table_name)
);

-- Platform-level defaults (tenant_id IS NULL = applies to all tenants)
INSERT INTO retention_policies
    (retention_class, table_name, retain_years, retain_days,
     anonymise_after_years, auto_purge, legal_basis, notes)
VALUES
    -- Compliance evidence: 7 years, never auto-purge (requires manual review)
    ('compliance', NULL,                7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(e)',
     'Compliance records must be retained to evidence certification history'),

    -- Specific compliance tables
    ('compliance', 'posture_controls',  7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Posture history required for audit trail'),
    ('compliance', 'isms_audits',       7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Audit records required for surveillance audits'),
    ('compliance', 'incidents',         7, 0, 5,     FALSE,
     'ISO 27001 A.5.26, GDPR Art.33',
     'Anonymise personal data after 5 years, retain incident record for 7'),
    ('compliance', 'document_findings', 7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Evidence of document evaluation retained'),

    -- Operational data: 5 years, auto-purge permitted after retention
    ('operational', NULL,               5, 0, 3,     TRUE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(e)',
     'Operational records retained 5 years, PII anonymised after 3'),
    ('operational', 'risks',            5, 0, 3,     TRUE,
     'ISO 27001 A.5.33', 'Risk register retained 5 years'),
    ('operational', 'vendors',          5, 0, 3,     TRUE,
     'ISO 27001 A.5.33, GDPR Art.28',
     'Processor agreements retained 5 years, contact data anonymised at 3'),
    ('operational', 'remediation_plans',5, 0, NULL,  TRUE,
     'ISO 27001 A.5.33', 'Remediation evidence retained 5 years'),

    -- Personal data: erasure on request, anonymise in place
    ('personal_data', NULL,             0, 0, NULL,  FALSE,
     'GDPR Art.17', 'Erasure on data subject request within 30 days'),
    ('personal_data', 'users',          0, 0, NULL,  FALSE,
     'GDPR Art.17', 'User accounts anonymised on erasure request or account closure'),

    -- Platform config: retain while active
    ('platform', NULL,                  0, 30, NULL, TRUE,
     'Contractual', 'Soft deleted on tenant offboarding, purged after 30 days'),

    -- Session data: 90 days
    ('session', NULL,                   0, 90, NULL, TRUE,
     'GDPR Art.5(1)(e), Storage limitation',
     'Conversation history auto-purged after 90 days')

ON CONFLICT (tenant_id, retention_class, table_name) DO NOTHING;

-- Fix: insert platform defaults with NULL tenant_id requires special handling
-- The UNIQUE constraint treats NULL as distinct — use a partial unique index instead
DROP INDEX IF EXISTS idx_retention_policies_default;
CREATE UNIQUE INDEX IF NOT EXISTS idx_retention_policies_default
    ON retention_policies (retention_class, COALESCE(table_name, ''))
    WHERE tenant_id IS NULL;


-- =============================================================================
-- SECTION 2: DELETION AUDIT LOG
-- Append-only record of every deletion operation.
-- This table is NEVER soft-deleted and NEVER purged.
-- RLS: tenants can read their own entries, no one can delete.
-- =============================================================================

CREATE TABLE IF NOT EXISTS deletion_log (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        REFERENCES tenants(id),  -- NULL = platform operation
    table_name      TEXT        NOT NULL,
    record_id       UUID        NOT NULL,
    deletion_type   TEXT        NOT NULL
        CHECK (deletion_type IN (
            'soft',         -- is_active set to FALSE
            'anonymise',    -- PII fields replaced with [anonymised]
            'purge',        -- physical row deletion after retention
            'erasure'       -- GDPR Art.17 data subject request
        )),
    reason          TEXT        NOT NULL
        CHECK (reason IN (
            'erasure_request',    -- GDPR Art.17 data subject request
            'retention_expired',  -- past retention_until date
            'tenant_offboarding', -- tenant leaving platform
            'admin',              -- manual admin action
            'test_data'           -- test/dev data cleanup
        )),
    requested_by    UUID        REFERENCES users(id),  -- NULL = system/scheduled
    executed_by     UUID        REFERENCES users(id),  -- NULL = system
    executed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retention_class TEXT        NOT NULL,
    record_snapshot JSONB,      -- SHA-256 hash of key fields (NOT the data itself)
    purge_scheduled TIMESTAMPTZ,-- when physical purge is scheduled
    purge_verified_at TIMESTAMPTZ, -- when purge completion was verified
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_deletion_log_tenant
    ON deletion_log (tenant_id, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_deletion_log_table_record
    ON deletion_log (table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_deletion_log_type
    ON deletion_log (deletion_type, executed_at DESC);

-- Deletion log is readable by tenants for their own records
-- but NO ROW can ever be deleted — enforced by policy
ALTER TABLE deletion_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY deletion_log_read ON deletion_log
    FOR SELECT
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
        OR tenant_id IS NULL
    );

-- Explicitly deny DELETE on deletion_log for the app user
REVOKE DELETE ON deletion_log FROM arioncomply_app;
GRANT SELECT, INSERT ON deletion_log TO arioncomply_app;


-- =============================================================================
-- SECTION 3: ADD SOFT DELETE COLUMNS TO ALL TENANT-SCOPED TABLES
--
-- Columns added to every table:
--   is_active:        FALSE when soft-deleted (RLS filters these out)
--   deleted_at:       when it was soft-deleted
--   deleted_by:       who deleted it
--   deletion_reason:  why (maps to deletion_log.reason values)
--   retention_class:  which retention policy applies
--   purge_after:      earliest date physical deletion is permitted
-- =============================================================================

-- ── COMPLIANCE tables (7 years) ──────────────────────────────────────────────

ALTER TABLE posture_controls
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE posture_history
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE posture_pending
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE isms_audits
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE document_sections
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE incident_timeline
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE incident_documents
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE incident_obligations
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE control_documents
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'compliance',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

-- ── OPERATIONAL tables (5 years) ─────────────────────────────────────────────

ALTER TABLE client_documents
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE assets
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE risks
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE vendors
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE remediation_plans
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE remediation_tasks
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE remediation_evidence
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'operational',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

-- ── PERSONAL DATA tables ─────────────────────────────────────────────────────

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID,        -- self-reference avoided
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'personal_data',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS anonymised_at    TIMESTAMPTZ; -- when PII was anonymised

ALTER TABLE user_roles
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'personal_data',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

-- ── PLATFORM tables ───────────────────────────────────────────────────────────

ALTER TABLE tenant_standards
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'platform',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE notifications
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'platform',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE client_facts
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'platform',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;

ALTER TABLE applicable_standards
    ADD COLUMN IF NOT EXISTS is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS deleted_by       UUID        REFERENCES users(id),
    ADD COLUMN IF NOT EXISTS deletion_reason  TEXT,
    ADD COLUMN IF NOT EXISTS retention_class  TEXT        NOT NULL DEFAULT 'platform',
    ADD COLUMN IF NOT EXISTS purge_after      TIMESTAMPTZ;


-- =============================================================================
-- SECTION 4: PERFORMANCE INDEXES FOR SOFT DELETE
-- Every table needs an index on is_active to avoid full scans
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_posture_controls_active
    ON posture_controls (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_posture_history_active
    ON posture_history (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_incidents_active
    ON incidents (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_client_documents_active
    ON client_documents (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_assets_active
    ON assets (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_risks_active
    ON risks (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_vendors_active
    ON vendors (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_active
    ON users (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_remediation_plans_active
    ON remediation_plans (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_isms_audits_active
    ON isms_audits (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_control_documents_active
    ON control_documents (tenant_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_tenant_standards_active
    ON tenant_standards (tenant_id, is_active) WHERE is_active = TRUE;


-- =============================================================================
-- SECTION 5: UPDATE RLS POLICIES
-- Every existing policy is dropped and recreated to include is_active = TRUE
-- Deleted records are invisible to application queries by default
-- Admin bypass: SET LOCAL role = arioncomply_admin (separate role with BYPASSRLS)
-- =============================================================================

-- Pattern applied to all tables with tenant_id + is_active:
--   DROP POLICY IF EXISTS tenant_isolation ON <table>;
--   CREATE POLICY tenant_isolation ON <table>
--       USING (
--           tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
--           AND is_active = TRUE
--       );

-- COMPLIANCE tables
DROP POLICY IF EXISTS tenant_isolation ON posture_controls;
CREATE POLICY tenant_isolation ON posture_controls
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON posture_history;
CREATE POLICY tenant_isolation ON posture_history
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON posture_pending;
CREATE POLICY tenant_isolation ON posture_pending
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON isms_audits;
CREATE POLICY tenant_isolation ON isms_audits
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON document_findings;
CREATE POLICY tenant_isolation ON document_findings
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON document_sections;
CREATE POLICY tenant_isolation ON document_sections
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON incidents;
CREATE POLICY tenant_isolation ON incidents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON incident_timeline;
CREATE POLICY tenant_isolation ON incident_timeline
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON incident_documents;
CREATE POLICY tenant_isolation ON incident_documents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON incident_obligations;
CREATE POLICY tenant_isolation ON incident_obligations
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS ctrl_docs_tenant_isolation ON control_documents;
CREATE POLICY tenant_isolation ON control_documents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

-- OPERATIONAL tables
DROP POLICY IF EXISTS tenant_isolation ON client_documents;
CREATE POLICY tenant_isolation ON client_documents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON assets;
CREATE POLICY tenant_isolation ON assets
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON risks;
CREATE POLICY tenant_isolation ON risks
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON vendors;
CREATE POLICY tenant_isolation ON vendors
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON remediation_plans;
CREATE POLICY tenant_isolation ON remediation_plans
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON remediation_tasks;
CREATE POLICY tenant_isolation ON remediation_tasks
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON remediation_evidence;
CREATE POLICY tenant_isolation ON remediation_evidence
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

-- PERSONAL DATA tables
DROP POLICY IF EXISTS tenant_isolation ON users;
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON user_roles;
CREATE POLICY tenant_isolation ON user_roles
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

-- PLATFORM tables
DROP POLICY IF EXISTS tenant_isolation ON tenant_standards;
CREATE POLICY tenant_isolation ON tenant_standards
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON client_facts;
CREATE POLICY tenant_isolation ON client_facts
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON notifications;
CREATE POLICY tenant_isolation ON notifications
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON applicable_standards;
CREATE POLICY tenant_isolation ON applicable_standards
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
           AND is_active = TRUE);

DROP POLICY IF EXISTS tenant_isolation ON ref_sequences;
CREATE POLICY tenant_isolation ON ref_sequences
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);
-- ref_sequences has no is_active — it's a counter, not a content record


-- =============================================================================
-- SECTION 6: SOFT DELETE TRIGGER FUNCTION
-- Automatically sets purge_after when a record is soft-deleted
-- Computes from retention_policies table
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_compute_purge_after()
RETURNS TRIGGER AS $$
DECLARE
    v_retain_years INT;
    v_retain_days  INT;
    v_class        TEXT;
BEGIN
    -- Only fire when transitioning to inactive
    IF OLD.is_active = TRUE AND NEW.is_active = FALSE THEN
        v_class := NEW.retention_class;

        -- Look up retention period: table-specific first, then class default
        SELECT retain_years, retain_days
        INTO   v_retain_years, v_retain_days
        FROM   retention_policies
        WHERE  tenant_id IS NULL
          AND  retention_class = v_class
          AND  table_name = TG_TABLE_NAME
        LIMIT 1;

        IF NOT FOUND THEN
            SELECT retain_years, retain_days
            INTO   v_retain_years, v_retain_days
            FROM   retention_policies
            WHERE  tenant_id IS NULL
              AND  retention_class = v_class
              AND  table_name IS NULL
            LIMIT 1;
        END IF;

        -- Compute purge_after
        IF v_retain_years > 0 THEN
            NEW.purge_after := NOW() + (v_retain_years || ' years')::INTERVAL;
        ELSIF v_retain_days > 0 THEN
            NEW.purge_after := NOW() + (v_retain_days || ' days')::INTERVAL;
        ELSE
            -- personal_data class: erasure request — no fixed purge window
            NEW.purge_after := NULL;
        END IF;

        NEW.deleted_at := NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all soft-deletable tables
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'posture_controls', 'posture_history', 'posture_pending',
        'isms_audits', 'document_findings', 'document_sections',
        'incidents', 'incident_timeline', 'incident_documents',
        'incident_obligations', 'control_documents',
        'client_documents', 'assets', 'risks', 'vendors',
        'remediation_plans', 'remediation_tasks', 'remediation_evidence',
        'users', 'user_roles',
        'tenant_standards', 'notifications', 'client_facts',
        'applicable_standards'
    ]
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS trg_compute_purge_after ON %I',
            t
        );
        EXECUTE format(
            'CREATE TRIGGER trg_compute_purge_after
             BEFORE UPDATE OF is_active ON %I
             FOR EACH ROW EXECUTE FUNCTION fn_compute_purge_after()',
            t
        );
    END LOOP;
END $$;


-- =============================================================================
-- SECTION 7: SCHEDULED PURGE FUNCTION
-- Called nightly by pg_cron or application scheduler
-- Physically deletes records past their purge_after date
-- Writes to deletion_log for every purged record
-- NEVER touches deletion_log itself
-- NEVER touches compliance-class records (require manual review)
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_purge_expired_records(
    p_dry_run BOOLEAN DEFAULT TRUE  -- TRUE = report only, FALSE = actually purge
) RETURNS TABLE (
    table_name      TEXT,
    records_purged  BIGINT,
    records_skipped BIGINT
) AS $$
DECLARE
    t           TEXT;
    v_count     BIGINT;
    v_skipped   BIGINT;
    v_class     TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        -- Only auto_purge = TRUE classes
        'assets', 'risks', 'vendors',
        'remediation_plans', 'remediation_tasks', 'remediation_evidence',
        'client_documents',
        'users', 'user_roles',
        'tenant_standards', 'notifications'
        -- NOT: posture_controls, isms_audits, incidents — compliance class, manual review
    ]
    LOOP
        IF p_dry_run THEN
            EXECUTE format(
                'SELECT count(*) FROM %I
                 WHERE is_active = FALSE
                   AND purge_after IS NOT NULL
                   AND purge_after < NOW()',
                t
            ) INTO v_count;
            v_skipped := 0;
        ELSE
            -- Log before purging
            EXECUTE format(
                'INSERT INTO deletion_log
                    (tenant_id, table_name, record_id, deletion_type,
                     reason, retention_class, executed_at)
                 SELECT tenant_id, %L, id, ''purge'',
                        ''retention_expired'', retention_class, NOW()
                 FROM %I
                 WHERE is_active = FALSE
                   AND purge_after IS NOT NULL
                   AND purge_after < NOW()',
                t, t
            );

            -- Physical delete
            EXECUTE format(
                'WITH deleted AS (
                    DELETE FROM %I
                    WHERE is_active = FALSE
                      AND purge_after IS NOT NULL
                      AND purge_after < NOW()
                    RETURNING 1
                 ) SELECT count(*) FROM deleted',
                t
            ) INTO v_count;

            v_skipped := 0;
        END IF;

        table_name     := t;
        records_purged := CASE WHEN p_dry_run THEN 0 ELSE v_count END;
        records_skipped:= CASE WHEN p_dry_run THEN v_count ELSE 0 END;
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Only superuser can run the purge function
REVOKE ALL ON FUNCTION fn_purge_expired_records(BOOLEAN) FROM PUBLIC;
REVOKE ALL ON FUNCTION fn_purge_expired_records(BOOLEAN) FROM arioncomply_app;


-- =============================================================================
-- SECTION 8: ERASURE REQUEST HANDLER
-- GDPR Art.17 — anonymise personal data in place
-- Retains the record structure, replaces PII fields with [anonymised]
-- Writes to deletion_log with type='erasure'
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_handle_erasure_request(
    p_tenant_id        UUID,
    p_data_subject_ref TEXT,        -- email or external reference of data subject
    p_requested_by     UUID,        -- user_id of person submitting request
    p_dry_run          BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    table_name      TEXT,
    records_found   BIGINT,
    action_taken    TEXT
) AS $$
BEGIN
    -- Users table — anonymise name and email
    table_name    := 'users';
    records_found := 0;
    action_taken  := CASE WHEN p_dry_run THEN 'would_anonymise' ELSE 'anonymised' END;

    SELECT count(*) INTO records_found
    FROM users
    WHERE tenant_id = p_tenant_id
      AND (email = p_data_subject_ref OR name = p_data_subject_ref)
      AND is_active = TRUE;

    IF NOT p_dry_run AND records_found > 0 THEN
        UPDATE users SET
            name          = '[anonymised]',
            email         = '[anonymised-' || id || ']',
            anonymised_at = NOW(),
            deletion_reason = 'erasure_request'
        WHERE tenant_id = p_tenant_id
          AND (email = p_data_subject_ref OR name = p_data_subject_ref);

        INSERT INTO deletion_log
            (tenant_id, table_name, record_id, deletion_type,
             reason, requested_by, executed_at, retention_class)
        SELECT p_tenant_id, 'users', id, 'erasure',
               'erasure_request', p_requested_by, NOW(), 'personal_data'
        FROM users
        WHERE tenant_id = p_tenant_id
          AND email = '[anonymised-' || id || ']';
    END IF;
    RETURN NEXT;

    -- Vendors table — anonymise contact information
    table_name    := 'vendors';
    SELECT count(*) INTO records_found
    FROM vendors
    WHERE tenant_id = p_tenant_id
      AND is_active = TRUE;
    -- Vendors are legal entities not data subjects — no anonymisation needed
    -- unless contact_name is a natural person
    action_taken := 'not_applicable';
    records_found := 0;
    RETURN NEXT;

END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- =============================================================================
-- SECTION 9: GRANTS
-- =============================================================================

GRANT SELECT, INSERT, UPDATE ON retention_policies TO arioncomply_app;
GRANT SELECT ON deletion_log TO arioncomply_app;
GRANT INSERT ON deletion_log TO arioncomply_app;
-- DELETE on deletion_log deliberately NOT granted (see Section 2)

-- Verify: check all tables have is_active column
-- SELECT table_name
-- FROM information_schema.columns
-- WHERE column_name = 'is_active'
--   AND table_schema = 'public'
-- ORDER BY table_name;
