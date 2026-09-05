-- schema_v115_applicability_and_scoping_history.sql
--
-- Ship 118'.b (2026-09-05) — audit tables for point-in-time posture
-- reconstruction. Fills the two "current-only" gaps flagged by Ship
-- 118'.a's coverage_notes:
--
--   applicability_status_log — one row per (tenant, standard, control)
--     status change. Wired into rag/scoping/applicability.py so every
--     derive_applicability() run records what changed + which rule
--     fired.
--
--   client_facts_log — one row per (tenant, column) fact change.
--     Wired into PUT /api/v1/tenant/facts + create_first_tenant() so
--     every scoping-fact declaration/derivation is time-ordered.
--
-- Both tables are append-only in spirit (no DELETE grant to app role),
-- match posture_status_log's shape (Ship 4'.b addendum classifies
-- posture_status_log as compliance-load-bearing), and use tenant FK
-- ON DELETE NO ACTION (auditor evidence must not silently disappear
-- if a tenant is later deleted).

BEGIN;

-- ── applicability_status_log ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.applicability_status_log (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID NOT NULL REFERENCES tenants(id) ON DELETE NO ACTION,
    standard_id    TEXT NOT NULL,
    control_ref    TEXT NOT NULL,
    status_before  TEXT     CHECK (status_before IS NULL OR status_before IN ('applicable', 'na')),
    status_after   TEXT NOT NULL CHECK (status_after IN ('applicable', 'na')),
    reason_before  TEXT,
    reason_after   TEXT,
    rule_id        TEXT,   -- from rag/scoping/applicability.py::RULES
    change_source  TEXT NOT NULL DEFAULT 'derive_applicability'
                   CHECK (change_source IN (
                       'derive_applicability',
                       'framework_enrol',
                       'manual',
                       'backfill'
                   )),
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by     UUID  -- user_id if manual; NULL for engine-driven changes
);

CREATE INDEX IF NOT EXISTS idx_applicability_log_tenant_time
    ON public.applicability_status_log (tenant_id, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_applicability_log_lookup
    ON public.applicability_status_log (tenant_id, standard_id, control_ref, changed_at DESC);

ALTER TABLE public.applicability_status_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS app_all_applicability_status_log ON public.applicability_status_log;
CREATE POLICY app_all_applicability_status_log
    ON public.applicability_status_log
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

-- App role: read + insert, NO delete/update (append-only)
GRANT SELECT, INSERT ON public.applicability_status_log TO arioncomply_app;
REVOKE UPDATE, DELETE ON public.applicability_status_log FROM arioncomply_app;


-- ── client_facts_log ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.client_facts_log (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID NOT NULL REFERENCES tenants(id) ON DELETE NO ACTION,
    column_name    TEXT NOT NULL,
    value_before   TEXT,   -- text-render of the previous value (may be NULL)
    value_after    TEXT,   -- text-render of the new value (may be NULL if column cleared)
    source_before  TEXT,   -- fact_source[col].source before change
    source_after   TEXT,   -- fact_source[col].source after change
    change_source  TEXT NOT NULL
                   CHECK (change_source IN (
                       'user_put',        -- PUT /api/v1/tenant/facts
                       'quickstart_init', -- create_first_tenant
                       'backfill_script', -- scripts/dev/backfill_*
                       'admin',           -- direct DB / admin tooling
                       'derivation'       -- system-inferred
                   )),
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by     UUID  -- user_id when known
);

CREATE INDEX IF NOT EXISTS idx_client_facts_log_tenant_time
    ON public.client_facts_log (tenant_id, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_client_facts_log_column
    ON public.client_facts_log (tenant_id, column_name, changed_at DESC);

ALTER TABLE public.client_facts_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS app_all_client_facts_log ON public.client_facts_log;
CREATE POLICY app_all_client_facts_log
    ON public.client_facts_log
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT ON public.client_facts_log TO arioncomply_app;
REVOKE UPDATE, DELETE ON public.client_facts_log FROM arioncomply_app;

COMMIT;
