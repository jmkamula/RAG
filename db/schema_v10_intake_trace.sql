-- ArionComply Schema v10 — Intake Trace Log
-- Adds: intake_trace_log table for document pipeline observability
-- Safe to run on top of v9 — no existing tables altered or dropped
--
-- Design:
--   One row per pipeline stage per document run.
--   All stages for one file share the same trace_id.
--   Trace writes are best-effort — pipeline never fails due to trace errors.
--
-- Stages: read | enrich | extract | write | complete | failed
-- Status: ok | error | skipped | manual_review

-- ── Table ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS intake_trace_log (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id            TEXT        NOT NULL,           -- groups all stages of one run
    tenant_id           UUID        NOT NULL REFERENCES tenants(id),
    upload_id           TEXT,                           -- document_uploads.id (may be null on early failure)
    filename            TEXT        NOT NULL,

    -- Stage identity
    stage               TEXT        NOT NULL
        CHECK (stage IN ('read','enrich','extract','write','complete','failed')),
    stage_status        TEXT        NOT NULL DEFAULT 'ok'
        CHECK (stage_status IN ('ok','error','skipped','manual_review')),

    -- Timing
    stage_ms            INTEGER     NOT NULL DEFAULT 0,  -- this stage duration
    total_ms            INTEGER     NOT NULL DEFAULT 0,  -- cumulative from start

    -- Read stage metrics
    token_estimate      INTEGER,
    page_count          INTEGER,
    section_count       INTEGER,

    -- Enrich stage metrics
    extraction_path     TEXT
        CHECK (extraction_path IN ('full','sections','manual','structured', NULL)),
    doc_type            TEXT,
    standard_ids        TEXT[],
    explicit_refs_found INTEGER,

    -- Extract stage metrics
    llm_calls           INTEGER,
    findings_raw        INTEGER,                        -- before dedup/filter
    findings_kept       INTEGER,                        -- after filter

    -- Write stage metrics
    findings_written    INTEGER,
    posture_created     INTEGER,
    posture_updated     INTEGER,
    posture_skipped     INTEGER,                        -- source guard blocked

    -- Error tracking
    error_type          TEXT,
    error_detail        TEXT,

    -- Metadata
    traced_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    retention_class     TEXT        NOT NULL DEFAULT 'operational',
    purge_after         TIMESTAMPTZ
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_intake_trace_trace_id
    ON intake_trace_log(trace_id);

CREATE INDEX IF NOT EXISTS idx_intake_trace_tenant_time
    ON intake_trace_log(tenant_id, traced_at DESC);

CREATE INDEX IF NOT EXISTS idx_intake_trace_errors
    ON intake_trace_log(tenant_id, error_type, traced_at DESC)
    WHERE error_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_intake_trace_slow
    ON intake_trace_log(tenant_id, total_ms DESC)
    WHERE total_ms > 10000;

CREATE INDEX IF NOT EXISTS idx_intake_trace_upload
    ON intake_trace_log(upload_id)
    WHERE upload_id IS NOT NULL;

-- ── RLS ───────────────────────────────────────────────────────────────────────
ALTER TABLE intake_trace_log ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'intake_trace_log'
          AND policyname = 'app_all_intake_trace'
    ) THEN
        CREATE POLICY app_all_intake_trace ON intake_trace_log
            FOR ALL TO arioncomply_app
            USING (true) WITH CHECK (true);
    END IF;
END $$;

-- ── Grants ────────────────────────────────────────────────────────────────────
GRANT SELECT, INSERT ON intake_trace_log TO arioncomply_app;

-- ── Convenience view: one row per file run ────────────────────────────────────
CREATE OR REPLACE VIEW v_intake_runs AS
SELECT
    trace_id,
    tenant_id,
    upload_id,
    filename,
    MAX(CASE WHEN stage = 'enrich'  THEN doc_type         END) AS doc_type,
    MAX(CASE WHEN stage = 'enrich'  THEN standard_ids::text END) AS standard_ids,
    MAX(CASE WHEN stage = 'enrich'  THEN extraction_path   END) AS extraction_path,
    MAX(CASE WHEN stage = 'read'    THEN token_estimate    END) AS token_estimate,
    MAX(CASE WHEN stage = 'extract' THEN findings_kept     END) AS findings_extracted,
    MAX(CASE WHEN stage = 'write'   THEN findings_written  END) AS findings_written,
    MAX(CASE WHEN stage = 'write'   THEN posture_created   END) AS posture_created,
    MAX(CASE WHEN stage = 'write'   THEN posture_updated   END) AS posture_updated,
    MAX(CASE WHEN stage = 'write'   THEN posture_skipped   END) AS posture_skipped,
    MAX(total_ms)                                               AS total_ms,
    MAX(error_type)                                             AS error_type,
    MAX(error_detail)                                           AS error_detail,
    bool_or(stage_status = 'error')                             AS had_error,
    MIN(traced_at)                                              AS started_at,
    MAX(traced_at)                                              AS completed_at
FROM intake_trace_log
GROUP BY trace_id, tenant_id, upload_id, filename;

GRANT SELECT ON v_intake_runs TO arioncomply_app;

