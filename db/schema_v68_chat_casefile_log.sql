-- schema_v68_chat_casefile_log.sql
--
-- Ship 2'.g of the case-file arc (2026-07-15).
--
-- Per-turn trace of the CaseFile → digest → repair pipeline for
-- rank_and_answer. Records how much the digest actually compressed
-- the prompt, which preservation events fired, and what footers
-- the repair pass appended.
--
-- Purpose: measure the Ship 2' rollout before flipping
-- CASEFILE_ENABLED=1 in production. We claim:
--   * ~10× prompt-token reduction vs the 21,731-avg baseline
--   * Preservation repair catches all stochastic ref/verdict drops
-- This table lets us verify both claims empirically.
--
-- Relationship to ai_call_log:
--   ai_call_log        — raw token counts + preview per LLM call
--   chat_casefile_log  — WHY those numbers are what they are for the
--                        rank_answer purpose (digest breakdown, repair
--                        events, case-file shape). Joined on request_id.
--
-- What lands here:
--   * case_file_summary — jsonb from CaseFile.summary()
--   * system_prompt_tokens / user_digest_tokens / total
--   * repair_events — [{kind, ref, detail}, ...]
--   * footers_added — literal footer strings appended
--   * casefile_enabled — was Ship 2' active this turn?
--
-- What does NOT land here:
--   * The full digest text — that's in ai_call_log.prompt_preview
--   * The full LLM answer — that's in the LangGraph session checkpoint
--   * Signal-level intent detection — that's in chat_consensus_log
--     from schema_v67

BEGIN;

CREATE TABLE IF NOT EXISTS chat_casefile_log (
    id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                uuid NOT NULL REFERENCES tenants(id),
    request_id               text,
    session_id               text,

    -- Turn identification
    query                    text NOT NULL,
    question_type            text,

    -- CaseFile shape — what data the digest saw. Keeps the summary
    -- diagnostic view from CaseFile.summary() so we can correlate
    -- token savings with case complexity without joining resolver
    -- traces. Compact: node counts + posture counts + xfw bridges.
    case_file_summary        jsonb NOT NULL,

    -- Prompt-size breakdown (approx tokens — measured via the
    -- approx_tokens() helper, not tiktoken, to keep the hot path
    -- cheap; ai_call_log carries the tiktoken-measured tokens_in
    -- when the LLM call actually fires).
    system_prompt_tokens     int,
    user_digest_tokens       int,
    total_prompt_tokens      int,

    -- Repair pass output. events_count is denormalised for indexing.
    repair_events            jsonb NOT NULL DEFAULT '[]'::jsonb,
    repair_events_count      int  NOT NULL DEFAULT 0,
    footers_added            text[] NOT NULL DEFAULT '{}',

    -- Feature-flag context. When rolling out gradually, this makes
    -- shadow-mode comparisons (run both paths, log both, only serve
    -- one) trivial to slice.
    casefile_enabled         bool NOT NULL DEFAULT FALSE,
    shadow_mode              bool NOT NULL DEFAULT FALSE,

    -- Performance breakdown
    digest_latency_ms        int,
    repair_latency_ms        int,
    total_latency_ms         int,

    -- Diagnostics
    error_type               text,
    error_detail             text,

    -- Timestamps + retention
    created_at               timestamptz NOT NULL DEFAULT NOW(),
    purge_after              timestamptz
);

CREATE INDEX IF NOT EXISTS idx_ccfl_tenant_time
    ON chat_casefile_log (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ccfl_session
    ON chat_casefile_log (session_id, created_at DESC)
    WHERE session_id IS NOT NULL;

-- Repair events are the primary tuning signal: high frequencies
-- indicate the digest or system prompt still leaks preservation
-- failures we should tighten upstream.
CREATE INDEX IF NOT EXISTS idx_ccfl_repaired
    ON chat_casefile_log (tenant_id, created_at DESC)
    WHERE repair_events_count > 0;

-- Feature-flag rollout tracking.
CREATE INDEX IF NOT EXISTS idx_ccfl_enabled
    ON chat_casefile_log (casefile_enabled, created_at DESC);

COMMENT ON TABLE chat_casefile_log IS
'Per-turn trace of the CaseFile → digest → repair pipeline. Used to measure prompt-token reduction + preservation-repair event frequency. Ship 2'' observability.';

COMMENT ON COLUMN chat_casefile_log.case_file_summary IS
'CaseFile.summary() diagnostic view: {query_len, question_type, cited_refs, primary_nodes, xfw_nodes, xfw_bridges, doc_contexts, posture_counts, active_session_refs}. Compact JSON for slicing without joining resolver traces.';

COMMENT ON COLUMN chat_casefile_log.repair_events IS
'[{kind: "missing_ref"|"missing_draft_near_ref"|"missing_verdict_near_ref"|"missing_bridge_footer", ref: "A.5.18", detail: "..."}]. High "missing_ref" rate = LLM dropping content; investigate whether the digest surfaced it.';

COMMENT ON COLUMN chat_casefile_log.casefile_enabled IS
'TRUE when Ship 2'' was active on this turn (CASEFILE_ENABLED=1). During rollout: compare token/repair distributions between enabled/disabled slices.';

COMMENT ON COLUMN chat_casefile_log.shadow_mode IS
'TRUE when both paths ran but only one was served — shadow comparison. When True, casefile_enabled indicates which path was measured, not which was served.';

-- Row-level security — tenant isolation.
ALTER TABLE chat_casefile_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chat_casefile_log_tenant_isolation ON chat_casefile_log;
CREATE POLICY chat_casefile_log_tenant_isolation ON chat_casefile_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT ON chat_casefile_log TO arioncomply_app;

COMMIT;
