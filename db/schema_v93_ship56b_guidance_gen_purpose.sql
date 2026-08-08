-- schema_v93 — Ship 56'.b (2026-08-05)
--
-- Add 'guidance_gen' to ai_call_log.purpose allowlist so the LLM-driven
-- per-MUST guidance generator (enrichment/guidance/generate_from_catalog.py)
-- can log its calls without hitting the CHECK constraint.
--
-- Follows the same idempotent DROP+ADD pattern as schema_v80 (Ship 5'.e
-- consensus_gatekeeper + enrichment_tier2).

ALTER TABLE ai_call_log DROP CONSTRAINT IF EXISTS ai_call_log_purpose_check;

ALTER TABLE ai_call_log ADD CONSTRAINT ai_call_log_purpose_check
    CHECK (purpose = ANY (ARRAY[
        'chat'::text,
        'classifier'::text,
        'polish'::text,
        'polish_short_circuit'::text,
        'rank_answer'::text,
        'compose'::text,
        'correct'::text,
        'verify'::text,
        'extractor'::text,
        'extractor_pass2'::text,
        'enricher'::text,
        'xfw_proposer'::text,
        'cascade'::text,
        'embedding_query'::text,
        'embedding_index'::text,
        'consensus_gatekeeper'::text,
        'enrichment_tier2'::text,
        'guidance_gen'::text,
        'other'::text
    ]));
