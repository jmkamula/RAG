-- schema_v67_chat_consensus_log.sql
--
-- Ship 1.11 of the retrieval-first consensus arc (2026-07-14).
--
-- Per-turn trace of ConsensusResult from rag.consensus.run_consensus.
-- Mirrors the observability pattern used for the intake critic-
-- verifier (ai_call_log): every consensus decision is logged so
-- we can tune floors/weights empirically instead of guessing.
--
-- What lands here:
--   * verdict (confident/ambiguous/insufficient)
--   * top refs + confidence + corroborator count
--   * inferred question_type + framework
--   * full audit trail of every signal (signals_json)
--   * flag for whether the legacy LLM classifier was needed
--   * clarification payload when the verdict was ambiguous
--
-- What does NOT land here:
--   * The actual answer or answer_text — those still land in
--     the LangGraph session checkpoints. This table is scoped
--     to the intent-detection layer only.

BEGIN;

CREATE TABLE IF NOT EXISTS chat_consensus_log (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             uuid NOT NULL REFERENCES tenants(id),
    request_id            text,
    session_id            text,

    -- Query being decided on
    query                 text NOT NULL,

    -- The verdict decides which branch the classify node takes
    -- confident    → skip LLM classifier, use consensus refs directly
    -- ambiguous    → deterministic clarify path
    -- insufficient → fall through to legacy LLM classifier
    verdict               text NOT NULL,

    -- Consensus outputs
    top_refs              text[],
    top_ref_confidence    numeric(6,3),
    corroborators         int,
    question_type         text,
    framework             text,

    -- Full audit trail — every SignalOutput serialised. Structured
    -- as a JSON array so we can drill in without joining another
    -- table. Compact: refs as arrays of [ref, weight] pairs.
    signals_json          jsonb NOT NULL,

    -- Diagnostics
    disagreement_notes    text[],
    clarification         jsonb,   -- populated when verdict='ambiguous'
    llm_fallback_used     bool NOT NULL DEFAULT FALSE,

    -- Performance
    latency_ms            int,

    -- Timestamps + retention
    created_at            timestamptz NOT NULL DEFAULT NOW(),
    purge_after           timestamptz,

    CONSTRAINT ccl_verdict_check
        CHECK (verdict IN ('confident','ambiguous','insufficient'))
);

CREATE INDEX IF NOT EXISTS idx_ccl_tenant_time
    ON chat_consensus_log (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ccl_verdict
    ON chat_consensus_log (verdict, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ccl_session
    ON chat_consensus_log (session_id, created_at DESC)
    WHERE session_id IS NOT NULL;

-- llm_fallback_used = TRUE is our tuning signal: too many =
-- floors/weights need adjusting.
CREATE INDEX IF NOT EXISTS idx_ccl_fallback
    ON chat_consensus_log (tenant_id, created_at DESC)
    WHERE llm_fallback_used = TRUE;

COMMENT ON TABLE chat_consensus_log IS
'Per-turn trace of the retrieval-first consensus layer. Used to tune ConsensusConfig weights + floors empirically. Mirrors ai_call_log observability pattern.';

COMMENT ON COLUMN chat_consensus_log.signals_json IS
'JSON array of {name, refs:[[ref,weight],...], question_type, framework, metadata, fired}. Full audit trail of what each of the 7 consensus signals contributed for this turn.';

COMMENT ON COLUMN chat_consensus_log.llm_fallback_used IS
'TRUE when the legacy LLM classifier fired because consensus was insufficient. High rates indicate floors need tuning or coverage gaps in the deterministic signals.';

-- Row-level security — tenant isolation like every other tenant-
-- scoped table in the schema.
ALTER TABLE chat_consensus_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chat_consensus_log_tenant_isolation ON chat_consensus_log;
CREATE POLICY chat_consensus_log_tenant_isolation ON chat_consensus_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT ON chat_consensus_log TO arioncomply_app;

COMMIT;
