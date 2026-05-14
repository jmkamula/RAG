-- =============================================================================
-- ArionComply — Schema v7
-- Incident Classifications
--
-- Replaces the single `incidents.incident_type` text column (long-term) with
-- a per-(standard, dimension) classification model. Each incident may carry
-- multiple classifications across standards; each (standard, dimension, value)
-- triple resolves via Neo4j (:ClassificationValue -[:MANIFESTS_AS]-> :Event)
-- to the Event(s) whose TRIGGERS_OBLIGATION set materialises obligations
-- into `incident_obligations`.
--
-- Background: see memory/incident_obligations_model.md (locked design).
--
-- This migration is purely ADDITIVE — only adds `incident_classifications`.
--
-- Three dead columns on `incidents` are slated for removal in a later
-- migration that also refreshes the `v_incidents_open` view (which currently
-- expands `i.*` to include them):
--   incidents.incident_type    — replaced by classifications
--   incidents.neo4j_synced     — reserved for abandoned "project Incident
--   incidents.neo4j_node_id      to Neo4j" idea
-- Doing those drops together (with the view refresh + importer rewrite)
-- avoids a broken intermediate state.
--
-- Apply:
--   psql arioncomply_compliance -f db/schema_v7.sql
-- =============================================================================

-- ── New table: incident_classifications ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS incident_classifications (
    incident_id      UUID NOT NULL REFERENCES incidents(id),
    tenant_id        UUID NOT NULL REFERENCES tenants(id),
    standard_id      TEXT NOT NULL,
    dimension        TEXT NOT NULL,
    value            TEXT NOT NULL,

    source           TEXT NOT NULL DEFAULT 'manual'
        CHECK (source IN ('workbook','manual','api','derived','llm')),
    confidence       NUMERIC(4,3),                         -- 0.000–1.000; NULL = curator-certain
    classified_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    classified_by    UUID REFERENCES users(id),

    -- soft-delete + retention (matches incident_obligations / incident_documents)
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at       TIMESTAMPTZ,
    deleted_by       UUID REFERENCES users(id),
    deletion_reason  TEXT,
    retention_class  TEXT NOT NULL DEFAULT 'compliance',
    purge_after      TIMESTAMPTZ,

    PRIMARY KEY (incident_id, standard_id, dimension, value)
);

CREATE INDEX IF NOT EXISTS idx_incident_classifications_tenant
    ON incident_classifications (tenant_id);

CREATE INDEX IF NOT EXISTS idx_incident_classifications_lookup
    ON incident_classifications (standard_id, dimension, value)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_incident_classifications_incident
    ON incident_classifications (incident_id)
    WHERE is_active = TRUE;

-- ── Row Level Security ──────────────────────────────────────────────────────

ALTER TABLE incident_classifications ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON incident_classifications;
CREATE POLICY tenant_isolation ON incident_classifications
    USING (tenant_id = (NULLIF(current_setting('app.tenant_id', TRUE), ''))::UUID
           AND is_active = TRUE);

-- ── Retention trigger ───────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_compute_purge_after ON incident_classifications;
CREATE TRIGGER trg_compute_purge_after
    BEFORE UPDATE OF is_active ON incident_classifications
    FOR EACH ROW EXECUTE FUNCTION fn_compute_purge_after();

-- ── App user grants ─────────────────────────────────────────────────────────
-- setup_local.sh grants DML on ALL TABLES at install time, but tables created
-- by later migrations need explicit grants. Without this, arioncomply_app
-- gets permission-denied on INSERT/UPDATE/SELECT.

DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'arioncomply_app') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE
            ON incident_classifications TO arioncomply_app;
    END IF;
END $$;

