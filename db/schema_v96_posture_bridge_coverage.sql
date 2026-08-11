-- schema_v96 — P/E/O framework role + bridge coverage attribution.
--
-- Ship 59'.a (2026-08-11). Extends the Ship 58' SSoT with:
--   1. framework_role denormalized on posture_must_verdicts (fast filter,
--      dashboards can group by role without joining catalog metadata)
--   2. new posture_must_bridge_coverage table capturing per-tenant
--      one-hop cross-framework bridge coverage — for each direct-satisfied
--      source MUST, one row per target MUST reachable via an
--      IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE edge with matching scope.
--
-- Engine remains unchanged. posture_controls.finding NOT touched by
-- bridge coverage. Bridge attribution is a parallel data layer surfaced
-- via the shared reader (rag.posture.must_verdicts); consumers opt in
-- to bridge awareness explicitly (checking MustVerdict.bridge_sources or
-- MustVerdict.state == 'bridged'). Default MustVerdict.satisfied remains
-- strict direct-only for backward compat.
--
-- Grain: (tenant_id, target_must_id, source_must_id, edge_type) UNIQUE.
-- Refresh: same cadence as posture_must_verdicts — after each engine walk
-- the writer replaces the tenant's bridge rows atomically.

-- ── 1. Framework role denormalization on posture_must_verdicts ──────────────

ALTER TABLE posture_must_verdicts
    ADD COLUMN IF NOT EXISTS framework_role text
    CHECK (framework_role IS NULL
        OR framework_role IN ('PROGRAM', 'EXTENSION', 'OBLIGATION', 'OTHER'));

CREATE INDEX IF NOT EXISTS idx_pmv_framework_role
    ON posture_must_verdicts (tenant_id, framework_role)
    WHERE framework_role IS NOT NULL;


-- ── 2. Bridge coverage table ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS posture_must_bridge_coverage (
    id                 bigserial   PRIMARY KEY,
    tenant_id          uuid        NOT NULL,

    -- The MUST being covered (auditor asks: "how is THIS covered?")
    target_must_id     text        NOT NULL,
    target_control_ref text        NOT NULL,
    target_standard_id text        NOT NULL,
    target_role        text        NOT NULL
        CHECK (target_role IN ('PROGRAM', 'EXTENSION', 'OBLIGATION', 'OTHER')),

    -- The MUST whose direct satisfaction is contributing coverage
    source_must_id     text        NOT NULL,
    source_control_ref text        NOT NULL,
    source_standard_id text        NOT NULL,
    source_role        text        NOT NULL
        CHECK (source_role IN ('PROGRAM', 'EXTENSION', 'OBLIGATION', 'OTHER')),

    -- The bridge edge type from Ship 1.7 xfw dedicated lane
    edge_type          text        NOT NULL
        CHECK (edge_type IN ('IMPLEMENTS', 'SUPPORTS', 'ENABLES', 'GOVERNANCE')),

    computed_at        timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_pmv_bridge_coverage
        UNIQUE (tenant_id, target_must_id, source_must_id, edge_type)
);

-- Forward query: "how is target X covered?"
CREATE INDEX IF NOT EXISTS idx_pmv_bridge_target
    ON posture_must_bridge_coverage (tenant_id, target_must_id);

-- Reverse query: "what does source Y contribute to?"
CREATE INDEX IF NOT EXISTS idx_pmv_bridge_source
    ON posture_must_bridge_coverage (tenant_id, source_must_id);

-- Framework-cross query: e.g. "how much OBLIGATION coverage comes from
-- PROGRAM evidence?"
CREATE INDEX IF NOT EXISTS idx_pmv_bridge_role_cross
    ON posture_must_bridge_coverage (tenant_id, source_role, target_role);


-- ── 3. RLS tenant isolation ─────────────────────────────────────────────────

ALTER TABLE posture_must_bridge_coverage ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pmv_bridge_tenant_isolation ON posture_must_bridge_coverage;
CREATE POLICY pmv_bridge_tenant_isolation ON posture_must_bridge_coverage
    USING      ((tenant_id)::text = current_setting('app.tenant_id', true))
    WITH CHECK ((tenant_id)::text = current_setting('app.tenant_id', true));

GRANT SELECT, INSERT, UPDATE, DELETE ON posture_must_bridge_coverage TO arioncomply_app;
GRANT USAGE ON SEQUENCE posture_must_bridge_coverage_id_seq TO arioncomply_app;
