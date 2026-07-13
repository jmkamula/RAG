-- schema_v64_fact_source_config.sql
--
-- UPDATES_FACT (2026-07-13): source-of-truth query per fact so
-- client_facts booleans stay fresh instead of drifting from initial
-- setup. Recompute worker reads this config, runs the source query
-- per fact per tenant, writes result to client_facts, logs the delta
-- to fact_recompute_log (and client_fact_change_log via the writer's
-- existing trigger, if any).
--
-- source_type variants (MVP):
--   posture    — check posture_controls for a specific (control_ref,
--                standard_id, finding). Config: {control_ref,
--                standard_id, exclude_findings?[]}.
--   evidence   — check document_findings for approved bindings on
--                a control (or any of a list). Config: {control_ref
--                or any_of_control_refs[], standard_id, min_count?}.
--   sql        — reserved for parameterised SQL against the app DB.
--                Config: {query} with {{tenant_id}} placeholder.
--   external   — reserved for future HTTP connectors (Odoo, Okta,
--                ServiceNow). Not implemented in MVP.
--   llm        — reserved for LLM-derived facts. Expensive; use rarely.
--
-- refresh_days is the recompute cadence. Scheduler (3b) reads this
-- and picks up facts past their last_recomputed_at + refresh_days.

BEGIN;

CREATE TABLE IF NOT EXISTS fact_source_config (
    id                 uuid           PRIMARY KEY DEFAULT gen_random_uuid(),
    fact_key           text           NOT NULL,       -- matches client_facts column name
    source_type        text           NOT NULL,
    source_query       text,                          -- SQL template for source_type='sql'
    source_config      jsonb          NOT NULL DEFAULT '{}',
    refresh_days       integer        NOT NULL DEFAULT 7,
    is_active          boolean        NOT NULL DEFAULT TRUE,
    description        text,                          -- human-readable purpose
    created_at         timestamptz    NOT NULL DEFAULT NOW(),
    updated_at         timestamptz    NOT NULL DEFAULT NOW(),
    CONSTRAINT fact_source_type_check
        CHECK (source_type IN ('sql','posture','evidence','external','llm'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_source_config_key
    ON fact_source_config (fact_key) WHERE is_active = TRUE;

COMMENT ON TABLE fact_source_config IS
'UPDATES_FACT: source-of-truth definition per client_facts key. Recompute worker uses this to refresh facts periodically.';

-- Per-tenant recompute tracking. Keyed by (tenant, fact) so we know
-- when each was last checked + what it was set to.
CREATE TABLE IF NOT EXISTS fact_recompute_log (
    id                 uuid           PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id          uuid           NOT NULL REFERENCES tenants(id),
    fact_key           text           NOT NULL,
    computed_value     boolean,                       -- NULL when query returned NULL/error
    prior_value        boolean,                       -- what client_facts said before
    changed            boolean        NOT NULL,       -- delta vs prior
    source_type        text           NOT NULL,
    error_type         text,
    error_detail       text,
    computed_at        timestamptz    NOT NULL DEFAULT NOW(),
    latency_ms         integer
);

CREATE INDEX IF NOT EXISTS idx_fact_recompute_tenant_fact_time
    ON fact_recompute_log (tenant_id, fact_key, computed_at DESC);

CREATE INDEX IF NOT EXISTS idx_fact_recompute_recent_changes
    ON fact_recompute_log (tenant_id, computed_at DESC)
 WHERE changed = TRUE;

COMMENT ON TABLE fact_recompute_log IS
'UPDATES_FACT: audit trail of every recompute. Feeds the trace UI and the scheduler past-due query.';

-- Seed a few DB-derivable facts for the MVP. Additional facts land
-- via later commits / operator config.
INSERT INTO fact_source_config (fact_key, source_type, source_config, refresh_days, description) VALUES
  ('uses_processors',
   'evidence',
   '{"control_ref": "B.8.2.1", "standard_id": "ISO27701:2019", "min_count": 1}'::jsonb,
   7,
   'Set TRUE when the tenant has at least 1 approved evidence on B.8.2.1 (customer/processor agreement).'),
  ('processes_personal_data',
   'evidence',
   '{"any_of_control_refs": ["A.7.2.1", "A.7.2.8", "B.8.2.6"], "standard_id": "ISO27701:2019", "min_count": 1}'::jsonb,
   14,
   'Set TRUE when the tenant has any approved PII processing evidence on the RoPA leaves.'),
  ('automated_decision_making',
   'posture',
   '{"control_ref": "A.7.3.10", "standard_id": "ISO27701:2019", "exclude_findings": ["N/A"]}'::jsonb,
   14,
   'Set TRUE when A.7.3.10 posture is anything except N/A.')
ON CONFLICT DO NOTHING;

GRANT SELECT ON fact_source_config TO arioncomply_app;
GRANT SELECT, INSERT ON fact_recompute_log TO arioncomply_app;

COMMIT;
