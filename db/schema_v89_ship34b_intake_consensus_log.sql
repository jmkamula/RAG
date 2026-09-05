-- schema_v89_ship34b_intake_consensus_log.sql
--
-- Ship 34'.b (2026-07-25) — telemetry for the Ship 33 extraction
-- consensus module. One row per doc processed through
-- rag/intake/consensus_extraction/. Enables threshold tuning +
-- weight iteration from production data post-Ship-35 cutover.
--
-- Design source: docs/memory/ship_33_prime_a_redux_extraction_consensus_design_2026_07_25.md
-- (§ Telemetry) — schema locked in Ship 34'.a design memo.
--
-- Retention: retention_class='diagnostic' per Ship 4'.b addendum
-- (schema_v79) audit-log classification. Sweep-eligible after 90d;
-- arioncomply_app has INSERT/SELECT/DELETE (same shape as
-- chat_casefile_log, chat_consensus_log, intake_trace_log).
--
-- RLS: standard tenant isolation policy — arioncomply_app never
-- bypasses; superuser (arioncomply) does. Callers must
-- set_config('app.tenant_id', ..., TRUE) before SELECT.

BEGIN;

CREATE TABLE IF NOT EXISTS intake_consensus_log (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                 UUID NOT NULL,
    upload_id                 UUID NOT NULL,
    logged_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Verdict counts (aggregator output; LLM arbiter may reclassify
    -- some arbiter → accept/drop, so n_arbiter here is the POST-LLM
    -- count, and n_arbiter_llm_accept/reject explain the movement)
    total_candidates          INT  NOT NULL,
    n_accept                  INT  NOT NULL,
    n_arbiter                 INT  NOT NULL,   -- remaining after LLM arbiter (usually 0)
    n_drop                    INT  NOT NULL,

    -- LLM arbiter movement — how many arbiter-zone candidates the
    -- LLM decided which way. n_arbiter_llm_accept + n_arbiter_llm_reject
    -- + (residual n_arbiter) = original arbiter count from aggregator.
    n_arbiter_llm_accept      INT  NOT NULL DEFAULT 0,
    n_arbiter_llm_reject      INT  NOT NULL DEFAULT 0,

    -- Per-signal fire counts. Shape:
    --   {"fingerprint_keyword": 121, "must_semantic_topk": 108, ...}
    signals_summary           JSONB NOT NULL,

    -- Optional per-candidate sample for tuning. Bounded (top 20 by
    -- score, plus all LLM-arbiter decisions). Shape:
    --   [{"leaf_id": ..., "must_id": ..., "score": ..., "signals": [...],
    --     "verdict": "accept|arbiter|drop", "llm_verdict": "accept|reject|null",
    --     "excerpt": "...", "must_text": "..."}, ...]
    -- Nullable — not every write needs the sample (only shadow-mode
    -- + tuning-mode writes).
    candidates_sample         JSONB,

    -- Cost + latency for this doc's consensus pass
    latency_ms                INT,
    cost_usd                  NUMERIC(10, 6),

    -- Retention classification — Ship 4'.b addendum pattern.
    retention_class           TEXT NOT NULL DEFAULT 'diagnostic',
    purge_after               TIMESTAMPTZ
);

-- Per-tenant tuning + threshold-iteration queries
CREATE INDEX IF NOT EXISTS idx_intake_consensus_log_tenant_time
    ON intake_consensus_log(tenant_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_intake_consensus_log_upload
    ON intake_consensus_log(upload_id);

-- Row-level security — tenant isolation like every other tenant-scoped
-- table. arioncomply_app never bypasses; superuser does.
ALTER TABLE intake_consensus_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS intake_consensus_log_tenant_isolation ON intake_consensus_log;
CREATE POLICY intake_consensus_log_tenant_isolation ON intake_consensus_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

-- Diagnostic table grants (matches Ship 4'.b addendum pattern)
GRANT SELECT, INSERT, DELETE ON intake_consensus_log TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: diagnostic log per Ship 121 classification; DELETE is intentional for retention sweep.

COMMENT ON TABLE intake_consensus_log IS
'Diagnostic log for Ship 33 extraction consensus module. One row per doc processed. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';

COMMIT;
