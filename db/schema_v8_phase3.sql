-- =============================================================================
-- ArionComply — Schema v8 (Phase 3)
-- TenantSourceRegistry + Request Trace Log
--
-- Purpose:
--   1. TenantSourceRegistry — tracks what data sources each tenant has active.
--      The resolver reads this at startup to know what it can call.
--      Adding a new source (e.g. ServiceNow) = one INSERT, no code change.
--
--   2. Request trace log — structured log of every resolver call.
--      Enables: per-tenant analytics, latency monitoring, source usage,
--      debugging of specific requests by request_id.
--
-- Design fits v6 principles:
--   - Soft delete on sources (tenant may disconnect, not delete)
--   - Append-only trace log (DELETE revoked)
--   - RLS on both tables
--   - Retention: sources = platform class, traces = operational (5 years)
-- =============================================================================


-- =============================================================================
-- SECTION 1: TENANT SOURCE REGISTRY
-- One row per data source per tenant.
-- The resolver checks this before calling any source.
-- =============================================================================

CREATE TABLE IF NOT EXISTS tenant_source_registry (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL REFERENCES tenants(id),

    -- Source identity
    source_id       TEXT        NOT NULL,   -- "questionnaire" | "uploaded_docs" |
                                            -- "servicenow" | "jira" | "lansweeper" | etc.
    source_type     TEXT        NOT NULL    -- "internal" | "document" | "api"
        CHECK (source_type IN ('internal', 'document', 'api', 'manual')),
    display_name    TEXT        NOT NULL,   -- human-readable: "ServiceNow CMDB"

    -- Connection details (for API sources)
    connection_url  TEXT,                   -- API base URL (NULL for internal/doc sources)
    auth_type       TEXT                    -- "oauth2" | "api_key" | "basic" | NULL
        CHECK (auth_type IS NULL OR auth_type IN ('oauth2', 'api_key', 'basic', 'none')),
    -- Credentials are NEVER stored here — use secrets manager reference
    secrets_ref     TEXT,                   -- e.g. "aws_secrets/arion/tenant_x/servicenow"

    -- Status
    status          TEXT        NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'pending_confirmation', 'disabled', 'error')),
    last_synced_at  TIMESTAMPTZ,
    last_error      TEXT,                   -- last error message if status='error'
    record_count    INT         NOT NULL DEFAULT 0,

    -- Who connected this source and when
    connected_by    UUID        REFERENCES users(id),
    connected_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Soft delete (v6 pattern)
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    deleted_at      TIMESTAMPTZ,
    deleted_by      UUID        REFERENCES users(id),
    deletion_reason TEXT,
    retention_class TEXT        NOT NULL DEFAULT 'platform',
    purge_after     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, source_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tenant_source_registry_tenant
    ON tenant_source_registry (tenant_id, status)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_tenant_source_registry_source
    ON tenant_source_registry (source_id, status)
    WHERE is_active = TRUE;

-- RLS
ALTER TABLE tenant_source_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_source_registry_isolation ON tenant_source_registry
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
        AND is_active = TRUE
    );

-- Grants
GRANT SELECT, INSERT, UPDATE ON tenant_source_registry TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE ON tenant_source_registry TO arioncomply_consultant;
REVOKE DELETE ON tenant_source_registry FROM arioncomply_app;
REVOKE DELETE ON tenant_source_registry FROM arioncomply_consultant;

-- Soft delete trigger (reuses fn_compute_purge_after from v6)
DROP TRIGGER IF EXISTS trg_compute_purge_after ON tenant_source_registry;
CREATE TRIGGER trg_compute_purge_after
    BEFORE UPDATE OF is_active ON tenant_source_registry
    FOR EACH ROW EXECUTE FUNCTION fn_compute_purge_after();


-- =============================================================================
-- SECTION 2: DEFAULT INTERNAL SOURCES (seeded for every new tenant)
-- These are created by the onboarding process for each tenant.
-- Shown here as reference data — actual inserts done by onboarding module.
-- =============================================================================

-- Reference: source_ids used by the resolver
-- 'posture_controls'  → Postgres posture table (always available)
-- 'vector_store'      → ChromaDB (available when docs are uploaded)
-- 'graph'             → Neo4j (available when standard data is loaded)
-- 'questionnaire'     → produced by free assessment
-- 'uploaded_docs'     → produced by doc_uploader.py


-- =============================================================================
-- SECTION 3: REQUEST TRACE LOG
-- Structured log of every resolver.resolve() call.
-- Append-only — supports analytics, debugging, and SLA monitoring.
-- Keyed by request_id — links to conversation history.
-- =============================================================================

CREATE TABLE IF NOT EXISTS request_trace_log (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id      TEXT        NOT NULL,   -- UUID from ResolveRequest.request_id
    tenant_id       UUID        NOT NULL REFERENCES tenants(id),

    -- Query context
    query_text      TEXT        NOT NULL,
    classifier_type TEXT        NOT NULL,   -- e.g. "gap_analysis"
    taxonomy_type   TEXT        NOT NULL,   -- e.g. "POSTURE_STATUS"
    handler_name    TEXT        NOT NULL,
    strategy        TEXT        NOT NULL,   -- e.g. "posture+vector+graph"
    topic_ref       TEXT,                   -- e.g. "A.5.18" if detected

    -- Retrieval policy (what was declared)
    policy_posture      BOOLEAN NOT NULL DEFAULT TRUE,
    policy_vector       BOOLEAN NOT NULL DEFAULT TRUE,
    policy_graph        BOOLEAN NOT NULL DEFAULT TRUE,
    policy_doc_inv      BOOLEAN NOT NULL DEFAULT FALSE,
    policy_short_circuit BOOLEAN NOT NULL DEFAULT FALSE,

    -- Retrieval results (what was actually used)
    node_ids_built      INT     NOT NULL DEFAULT 0,
    nodes_primary       INT     NOT NULL DEFAULT 0,
    nodes_secondary     INT     NOT NULL DEFAULT 0,
    vector_hits         INT     NOT NULL DEFAULT 0,
    doc_contexts        INT     NOT NULL DEFAULT 0,
    posture_ids_used    TEXT[], -- array of control refs used (not UUIDs)
    vector_top_scores   JSONB,  -- [{node_id, score}, ...] top 3

    -- Posture state at query time
    posture_total       INT     NOT NULL DEFAULT 0,
    posture_nc          INT     NOT NULL DEFAULT 0,
    posture_ofi         INT     NOT NULL DEFAULT 0,
    posture_confirmed   INT     NOT NULL DEFAULT 0,
    posture_draft       INT     NOT NULL DEFAULT 0,

    -- Answer
    short_circuit       BOOLEAN NOT NULL DEFAULT FALSE,
    answer_source       TEXT    NOT NULL DEFAULT 'llm',
                                -- "llm" | "postgres" | "short_circuit"

    -- Performance
    neo4j_ms            INT     NOT NULL DEFAULT 0,
    vector_ms           INT     NOT NULL DEFAULT 0,
    postgres_ms         INT     NOT NULL DEFAULT 0,
    total_ms            INT     NOT NULL DEFAULT 0,

    -- Error (NULL = success)
    error_type          TEXT,
    error_hint          TEXT,

    -- When
    traced_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Retention
    retention_class     TEXT    NOT NULL DEFAULT 'operational',
    purge_after         TIMESTAMPTZ
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_request_trace_tenant_time
    ON request_trace_log (tenant_id, traced_at DESC);

CREATE INDEX IF NOT EXISTS idx_request_trace_request_id
    ON request_trace_log (request_id);

CREATE INDEX IF NOT EXISTS idx_request_trace_taxonomy
    ON request_trace_log (tenant_id, taxonomy_type, traced_at DESC);

CREATE INDEX IF NOT EXISTS idx_request_trace_errors
    ON request_trace_log (tenant_id, error_type, traced_at DESC)
    WHERE error_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_request_trace_slow
    ON request_trace_log (tenant_id, total_ms DESC)
    WHERE total_ms > 5000;

-- RLS
ALTER TABLE request_trace_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY request_trace_log_isolation ON request_trace_log
    FOR SELECT
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
    );

-- App can INSERT traces; no one can delete (operational audit log)
GRANT SELECT, INSERT ON request_trace_log TO arioncomply_app;
GRANT SELECT ON request_trace_log TO arioncomply_consultant;
REVOKE DELETE ON request_trace_log FROM arioncomply_app;
REVOKE DELETE ON request_trace_log FROM PUBLIC;

-- Block deletes at trigger level (same pattern as confirmation_log)
CREATE OR REPLACE FUNCTION fn_block_request_trace_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'request_trace_log is append-only — deletions not permitted. '
        'request_id: %, traced_at: %',
        OLD.request_id, OLD.traced_at
    USING ERRCODE = '23000';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_block_request_trace_delete ON request_trace_log;
CREATE TRIGGER trg_block_request_trace_delete
    BEFORE DELETE ON request_trace_log
    FOR EACH ROW EXECUTE FUNCTION fn_block_request_trace_delete();

-- Purge after 5 years (operational class) — auto_purge = TRUE
-- Trigger reuses fn_compute_purge_after from v6
DROP TRIGGER IF EXISTS trg_compute_purge_after_trace ON request_trace_log;
-- Note: request_trace_log uses purge_after directly (no is_active column)
-- Purge is handled by the nightly fn_purge_expired_records() — add to its list


-- =============================================================================
-- SECTION 4: ANALYTICS VIEWS
-- Pre-built views for the platform dashboard and SLA monitoring.
-- =============================================================================

-- Per-tenant query volume and latency over last 30 days
CREATE OR REPLACE VIEW v_tenant_request_stats AS
SELECT
    tenant_id,
    taxonomy_type,
    COUNT(*)                                AS total_requests,
    ROUND(AVG(total_ms))                    AS avg_latency_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_ms)) AS p95_latency_ms,
    MAX(total_ms)                           AS max_latency_ms,
    COUNT(*) FILTER (WHERE error_type IS NOT NULL) AS error_count,
    COUNT(*) FILTER (WHERE short_circuit = TRUE)   AS short_circuit_count,
    MIN(traced_at)                          AS first_request,
    MAX(traced_at)                          AS last_request
FROM request_trace_log
WHERE traced_at >= NOW() - INTERVAL '30 days'
GROUP BY tenant_id, taxonomy_type
ORDER BY tenant_id, total_requests DESC;

GRANT SELECT ON v_tenant_request_stats TO arioncomply_app;
GRANT SELECT ON v_tenant_request_stats TO arioncomply_consultant;

-- Source usage — which sources are being called and how often
CREATE OR REPLACE VIEW v_source_usage AS
SELECT
    tenant_id,
    strategy,
    COUNT(*)                                AS request_count,
    ROUND(AVG(total_ms))                    AS avg_latency_ms,
    ROUND(AVG(nodes_primary + nodes_secondary)) AS avg_nodes_returned,
    ROUND(AVG(vector_hits))                 AS avg_vector_hits
FROM request_trace_log
WHERE traced_at >= NOW() - INTERVAL '30 days'
GROUP BY tenant_id, strategy
ORDER BY tenant_id, request_count DESC;

GRANT SELECT ON v_source_usage TO arioncomply_app;
GRANT SELECT ON v_source_usage TO arioncomply_consultant;

-- Slow queries (> 15s) — for latency investigation
CREATE OR REPLACE VIEW v_slow_requests AS
SELECT
    request_id,
    tenant_id,
    taxonomy_type,
    strategy,
    total_ms,
    neo4j_ms,
    vector_ms,
    postgres_ms,
    nodes_primary + nodes_secondary         AS total_nodes,
    vector_hits,
    traced_at
FROM request_trace_log
WHERE total_ms > 15000
  AND traced_at >= NOW() - INTERVAL '7 days'
ORDER BY total_ms DESC;

GRANT SELECT ON v_slow_requests TO arioncomply_app;
GRANT SELECT ON v_slow_requests TO arioncomply_consultant;


-- =============================================================================
-- SECTION 5: RETENTION POLICIES
-- =============================================================================

INSERT INTO retention_policies
    (retention_class, table_name, retain_years, retain_days,
     anonymise_after_years, auto_purge, legal_basis, notes)
VALUES
    ('operational', 'request_trace_log', 5, 0, NULL, TRUE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(e)',
     'Request traces retained 5 years for audit and performance analysis. '
     'Auto-purge permitted after retention period.'),

    ('platform', 'tenant_source_registry', 0, 30, NULL, TRUE,
     'Contractual',
     'Source registrations soft-deleted on disconnection, '
     'purged 30 days after soft delete.')
ON CONFLICT DO NOTHING;


-- =============================================================================
-- SECTION 6: GRANTS SUMMARY
-- =============================================================================

-- arioncomply_app:        INSERT traces, SELECT traces + source registry
-- arioncomply_consultant: SELECT traces + source registry, INSERT/UPDATE sources
-- arioncomply_admin:      Full access via BYPASSRLS
-- No one can DELETE from request_trace_log (trigger + REVOKE, two layers)
