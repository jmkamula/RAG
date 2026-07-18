-- schema_v80_ship5e_ai_call_log_purpose_allowlist.sql
--
-- Ship 5'.e (2026-07-18) — close the last INFORMATIONAL finding
-- from the Ship 5'.a LLM audit.
--
-- `ai_call_log_purpose_check` had been throwing constraint-violation
-- warnings for months because two purpose values used in production
-- code weren't in the allowlist:
--
--   consensus_gatekeeper  (Ship 1 consensus arc — bounded LLM arbiter
--                          in rag/consensus/gatekeeper.py)
--   enrichment_tier2      (Ship 5'.c — tier2_generator's migration
--                          off direct OpenAI to llm_client)
--
-- Both writes silently failed via ai_trace's error-swallow, which
-- means we've been missing ~5-15% of LLM-call telemetry (chat
-- gatekeeper calls + all tier2 enrichment runs).
--
-- Add both to the CHECK. Existing rows with any legacy purpose
-- value are unaffected — CHECK only applies to future INSERTs.

BEGIN;

ALTER TABLE ai_call_log
    DROP CONSTRAINT IF EXISTS ai_call_log_purpose_check;

ALTER TABLE ai_call_log
    ADD CONSTRAINT ai_call_log_purpose_check
    CHECK (purpose = ANY (ARRAY[
        'chat',
        'classifier',
        'polish',
        'polish_short_circuit',
        'rank_answer',
        'compose',
        'correct',
        'verify',
        'extractor',
        'extractor_pass2',
        'enricher',
        'xfw_proposer',
        'cascade',
        'embedding_query',
        'embedding_index',
        'consensus_gatekeeper',
        'enrichment_tier2',
        'other'
    ]));

COMMENT ON COLUMN ai_call_log.purpose IS
'Tag identifying which pipeline stage made the LLM call. Kept in sync with rag/llm_client.py callers. Adding a new purpose? Bump this allowlist in the same migration that lands the new call site. See [[ship-5-prime-e-ai-call-log-purpose-allowlist-2026-07-18]].';

COMMIT;
