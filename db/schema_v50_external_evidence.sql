-- schema_v50_external_evidence.sql — cite-mode v1 (3 tables)
--
-- Implements the cited-evidence path per [[product-principle-evidence-
-- stored-vs-cited]]. ArionComply tracks WHERE evidence lives + freshness
-- + ownership instead of holding a duplicate copy. Three tables:
--
--   1. tenant_external_system  — per (tenant, system) registry of source
--      systems the tenant uses for compliance evidence (Odoo HR, Azure
--      AD, ServiceNow CMDB, etc.). One row per source; many cites can
--      reference it.
--
--   2. external_evidence_source — per-MUST cite rows. Each binds one
--      checklist_item (must_id) to one source (system_id). UI groups
--      by (system_id, leaf_id) for tenant + auditor display; data
--      model stays atomic for engine queries.
--
--   3. external_evidence_verification_log — append-only audit history
--      keyed by (system_id, leaf_id, verified_at). One verification
--      event covers ALL cites in the (system, leaf) group; tenant
--      writes a single 'changes_detected' attestation.
--
-- All RLS-scoped. Soft-delete via is_active on cites + systems; the
-- verification log is append-only.

BEGIN;

-- ── 1. Tenant external system registry ────────────────────────────────────
CREATE TABLE IF NOT EXISTS tenant_external_system (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID         NOT NULL,
    system_name           TEXT         NOT NULL,
    -- e.g. "Odoo HR" / "Azure AD" / "ServiceNow CMDB"

    system_url            TEXT,
    -- Where in the system to look. Optional but recommended for audit.

    owner_user_id         UUID,
    -- Named responsible person (FK to users.id). Nullable for v1
    -- (tenant can register a system before assigning a named owner).

    default_cadence_days  INTEGER      NOT NULL DEFAULT 365,
    -- Default verification cadence applied to new cites for this system.
    -- Per-cite cadence_days overrides this on a per-MUST basis.

    covers_evidence_types TEXT[]       NOT NULL DEFAULT ARRAY[]::TEXT[],
    -- The evidence_types this system is OFFERED FOR when the UI picks a
    -- source for a leaf. E.g. {"register", "record"} for an HR system.
    -- Empty array = offered for all cite-acceptable types.

    is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    created_by            UUID,
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_by            UUID,

    CONSTRAINT tenant_external_system_cadence_positive
        CHECK (default_cadence_days >= 1 AND default_cadence_days <= 3650)
);

-- Partial unique: only active rows; lets tenants re-create a system
-- they previously deleted (new row, new id; old row remains for audit
-- but no longer collides on the name).
CREATE UNIQUE INDEX IF NOT EXISTS tenant_external_system_unique_name_active
    ON tenant_external_system(tenant_id, system_name) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_tenant_external_system_tenant
    ON tenant_external_system(tenant_id) WHERE is_active = TRUE;

ALTER TABLE tenant_external_system ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON tenant_external_system;
CREATE POLICY tenant_isolation ON tenant_external_system
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_external_system TO arioncomply_app;

COMMENT ON TABLE  tenant_external_system IS
    'Per-tenant registry of external systems used as compliance evidence sources. One row per (tenant, system). Many cites reference each row.';
COMMENT ON COLUMN tenant_external_system.covers_evidence_types IS
    'Evidence types this system is offered for in cite-source pickers. Empty = offered for all cite-acceptable types.';


-- ── 2. Per-MUST cite rows ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS external_evidence_source (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID         NOT NULL,
    must_id               TEXT         NOT NULL,
    leaf_id               TEXT         NOT NULL,
    system_id             UUID         NOT NULL REFERENCES tenant_external_system(id),

    cadence_days          INTEGER      NOT NULL,
    -- Per-cite override of the system default. Set at create time
    -- (typically defaulted from leaf.freshness_days when set, else
    -- from system.default_cadence_days).

    per_must_note         TEXT,
    -- Optional: how this specific MUST is captured in the source.

    last_verified_at      TIMESTAMPTZ,
    next_review_due       TIMESTAMPTZ,
    -- next_review_due = last_verified_at + cadence_days; recomputed on
    -- each verification. Application-maintained (no generated column —
    -- avoids edge cases on NULL last_verified_at).

    is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    created_by            UUID,
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_by            UUID,

    CONSTRAINT external_evidence_source_cadence_positive
        CHECK (cadence_days >= 1 AND cadence_days <= 3650),
    CONSTRAINT external_evidence_source_must_id_format
        CHECK (must_id ~ '^item:[A-Za-z0-9.]+:[a-z0-9_]+$'),
    CONSTRAINT external_evidence_source_leaf_id_format
        CHECK (leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$')
);

-- Partial unique on (tenant, must, system) — only active rows. Lets a
-- tenant re-cite a MUST from the same system after deletion without
-- collision (new row, new id; old row preserved for audit).
CREATE UNIQUE INDEX IF NOT EXISTS external_evidence_source_unique_active
    ON external_evidence_source(tenant_id, must_id, system_id) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_external_evidence_source_tenant_leaf
    ON external_evidence_source(tenant_id, leaf_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_external_evidence_source_tenant_must
    ON external_evidence_source(tenant_id, must_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_external_evidence_source_review_due
    ON external_evidence_source(tenant_id, next_review_due) WHERE is_active = TRUE;

ALTER TABLE external_evidence_source ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON external_evidence_source;
CREATE POLICY tenant_isolation ON external_evidence_source
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE, DELETE ON external_evidence_source TO arioncomply_app;

COMMENT ON TABLE  external_evidence_source IS
    'Per-MUST cite rows. Each binds one checklist_item to one source system. UI groups by (system_id, leaf_id) for display.';
COMMENT ON COLUMN external_evidence_source.next_review_due IS
    'last_verified_at + cadence_days. Application-maintained on each verification.';


-- ── 3. Verification log (append-only audit) ──────────────────────────────
CREATE TABLE IF NOT EXISTS external_evidence_verification_log (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID         NOT NULL,
    system_id             UUID         NOT NULL REFERENCES tenant_external_system(id),
    leaf_id               TEXT         NOT NULL,

    verified_at           TIMESTAMPTZ  NOT NULL DEFAULT now(),
    verified_by           UUID         NOT NULL,

    changes_detected      TEXT         NOT NULL,
    -- Mandatory audit-grade payload — what changed since last
    -- verification. Tenant cannot rubber-stamp; forced to think.

    sample_upload_id      UUID,
    -- Optional FK to document_uploads — sample export attached to
    -- this verification (extends auditor confidence).

    note                  TEXT,
    -- Optional free-text addition. Not enforced.

    -- Counts what was covered at the moment of verification
    -- (denormalised — read-only view; the cite rows are the truth).
    musts_covered_count   INTEGER      NOT NULL DEFAULT 0,

    CONSTRAINT external_evidence_verification_log_changes_nonempty
        CHECK (length(trim(changes_detected)) > 0),
    CONSTRAINT external_evidence_verification_log_leaf_id_format
        CHECK (leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$')
);

CREATE INDEX IF NOT EXISTS idx_external_evidence_verification_log_tenant_leaf
    ON external_evidence_verification_log(tenant_id, leaf_id, verified_at DESC);
CREATE INDEX IF NOT EXISTS idx_external_evidence_verification_log_system
    ON external_evidence_verification_log(tenant_id, system_id, verified_at DESC);

ALTER TABLE external_evidence_verification_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON external_evidence_verification_log;
CREATE POLICY tenant_isolation ON external_evidence_verification_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

-- Append-only — no UPDATE / DELETE grant (audit log integrity).
GRANT SELECT, INSERT ON external_evidence_verification_log TO arioncomply_app;

COMMENT ON TABLE external_evidence_verification_log IS
    'Append-only audit history of cite verifications. One row per (system, leaf, verify event). changes_detected REQUIRED — forces real review.';

COMMIT;
