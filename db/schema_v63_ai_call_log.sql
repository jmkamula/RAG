-- schema_v63_ai_call_log.sql
--
-- Wave 4b (2026-07-10): Traceable AI use. Every LLM/embedding call
-- from runtime pipelines lands in ai_call_log with model, tokens,
-- cost, latency, purpose, and provenance links (upload_id / session_id
-- / request_id). Enables:
--   - Auditor-ready inventory of every AI call the platform made per
--     tenant per day
--   - Cost accounting per purpose (extractor / chat / classifier / etc.)
--   - Latency + error tracking as a first-class signal alongside
--     request_trace_log and intake_trace_log
--   - Grounds for the Wave 4c tenant execution trace UI
--
-- Retention: 365 days by default (retention_class='operational').
-- Prompt + response are stored as SHA256 hashes plus a truncated
-- preview (500 chars) — the hash is stable across identical calls
-- (dedup / cache-hit analysis), the preview supports diagnostics
-- without persisting full PII-bearing content long-term.

BEGIN;

CREATE TABLE IF NOT EXISTS ai_call_log (
    id                uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         uuid          REFERENCES tenants(id),
    called_at         timestamptz   NOT NULL DEFAULT NOW(),

    -- What was called
    purpose           text          NOT NULL,
    provider          text          NOT NULL,
    model             text          NOT NULL,
    latency_ms        integer,

    -- Resource usage
    tokens_in         integer,
    tokens_out        integer,
    cost_usd          numeric(12, 6),

    -- Content fingerprints (SHA256 hex) — full content not stored
    prompt_hash       text,
    prompt_preview    text,
    response_hash     text,
    response_preview  text,

    -- Error state
    error_type        text,   -- 'rate_limit' | 'timeout' | 'api_error' | 'client_error' | NULL
    error_detail      text,

    -- Provenance links — how this call ties into other logs
    upload_id         uuid,
    session_id        text,
    request_id        text,

    metadata          jsonb         NOT NULL DEFAULT '{}',

    -- Retention
    retention_class   text          NOT NULL DEFAULT 'operational',
    purge_after       timestamptz,

    CONSTRAINT ai_call_log_purpose_check
        CHECK (purpose IN (
            'chat', 'classifier', 'polish', 'polish_short_circuit',
            'extractor', 'extractor_pass2', 'enricher',
            'xfw_proposer', 'cascade',
            'embedding_query', 'embedding_index',
            'other'
        )),
    CONSTRAINT ai_call_log_provider_check
        CHECK (provider IN ('openai', 'anthropic', 'other'))
);

CREATE INDEX IF NOT EXISTS idx_ai_call_log_tenant_time
    ON ai_call_log (tenant_id, called_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_call_log_purpose_time
    ON ai_call_log (purpose, called_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_call_log_errors
    ON ai_call_log (tenant_id, called_at DESC)
 WHERE error_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_call_log_upload
    ON ai_call_log (upload_id) WHERE upload_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_call_log_session
    ON ai_call_log (session_id) WHERE session_id IS NOT NULL;

COMMENT ON TABLE ai_call_log IS
'Wave 4b: per-LLM-call trace. One row per runtime AI call (extractor / classifier / chat / enricher / xfw / embeddings). Provider-neutral. Provenance links (upload_id / session_id / request_id) tie into intake_trace_log + request_trace_log.';

-- RLS: tenants can see their own; admin sees all
ALTER TABLE ai_call_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY app_all_ai_call_log ON ai_call_log
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

CREATE POLICY tenant_isolation_ai_call_log ON ai_call_log
    USING (tenant_id IS NULL
           OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);

GRANT SELECT, INSERT, UPDATE ON ai_call_log TO arioncomply_app;

COMMIT;
