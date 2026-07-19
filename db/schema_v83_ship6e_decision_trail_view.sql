-- schema_v83_ship6e_decision_trail_view.sql
--
-- Ship 6'.e (2026-07-19) — joined LLM decision-trail view.
--
-- One row per chat turn, joining:
--   chat_casefile_log   (spine — one row per turn)
--   chat_consensus_log  (0..1 rows per turn)
--   ai_call_log         (aggregated across all LLM calls in the turn)
--
-- The join key is `request_id`, stamped by
-- `api_server.py::set_trace_context()` at chat request entry and
-- picked up transparently by every internal LLM writer via
-- `rag.ai_trace.current_request_id()` (Ship 6'.e wire-up).
--
-- Rows are still generated when request_id is NULL (e.g. eval-
-- harness paths that don't stamp a request id) — the view returns
-- them with the consensus/ai_call sides empty; auditors filter
-- on request_id IS NOT NULL to isolate real chat traffic.
--
-- The view respects tenant-RLS on all three source tables. Any
-- caller reading it MUST have `app.tenant_id` GUC set (arioncomply_app
-- follows this convention already).
--
-- No indexes are added — source tables already have per-tenant +
-- created_at btree indexes, and this view has no persistent
-- storage of its own.

BEGIN;

DROP VIEW IF EXISTS chat_llm_decision_trail;

CREATE VIEW chat_llm_decision_trail AS
SELECT
    cf.id                       AS casefile_log_id,
    cf.tenant_id                AS tenant_id,
    cf.request_id               AS request_id,
    cf.session_id               AS session_id,
    cf.created_at               AS turn_at,
    cf.query                    AS query,
    cf.question_type            AS question_type,

    -- Consensus decision (Ship 1)
    cs.verdict                  AS consensus_verdict,
    cs.top_refs                 AS consensus_top_refs,
    cs.top_ref_confidence       AS consensus_top_conf,
    cs.corroborators            AS consensus_corroborators,
    cs.framework                AS consensus_framework,
    cs.llm_fallback_used        AS consensus_llm_fallback,

    -- Case-file preservation (Ship 2')
    cf.system_prompt_tokens     AS prompt_tokens_system,
    cf.user_digest_tokens       AS prompt_tokens_digest,
    cf.total_prompt_tokens      AS prompt_tokens_total,
    cf.repair_events_count      AS repair_events_count,
    cf.footers_added            AS footers_added,
    cf.digest_latency_ms        AS digest_latency_ms,
    cf.repair_latency_ms        AS repair_latency_ms,
    cf.total_latency_ms         AS total_latency_ms,

    -- Ship 6'.d claim scan
    cf.claim_events_count       AS claim_events_count,
    cf.claim_events             AS claim_events,
    LENGTH(cf.answer_text)      AS answer_len,

    -- LLM-call aggregate (Ship 5'.e purpose allowlist now covers all)
    llm.n_calls                 AS llm_n_calls,
    llm.tokens_in_total         AS llm_tokens_in,
    llm.tokens_out_total        AS llm_tokens_out,
    llm.cost_total              AS llm_cost_usd,
    llm.purposes                AS llm_purposes,
    llm.models                  AS llm_models

FROM chat_casefile_log cf
LEFT JOIN chat_consensus_log cs
       ON cs.request_id = cf.request_id
      AND cs.tenant_id  = cf.tenant_id
LEFT JOIN LATERAL (
    SELECT
        COUNT(*)::int                                       AS n_calls,
        COALESCE(SUM(al.tokens_in), 0)::int                 AS tokens_in_total,
        COALESCE(SUM(al.tokens_out), 0)::int                AS tokens_out_total,
        COALESCE(SUM(al.cost_usd), 0)::numeric(12,6)        AS cost_total,
        ARRAY_AGG(DISTINCT al.purpose ORDER BY al.purpose)  AS purposes,
        ARRAY_AGG(DISTINCT al.model   ORDER BY al.model)    AS models
      FROM ai_call_log al
     WHERE al.request_id = cf.request_id
       AND al.tenant_id  = cf.tenant_id
) llm ON TRUE
WHERE cf.request_id IS NOT NULL;

COMMENT ON VIEW chat_llm_decision_trail IS
'Ship 6''.e (2026-07-19): one row per chat turn joining chat_casefile_log ⋈ chat_consensus_log ⋈ ai_call_log on request_id. Auditor + engineer surface for tracing a full LLM decision trail. See [[ship-6-prime-e-decision-trail-view-2026-07-19]].';

COMMIT;
