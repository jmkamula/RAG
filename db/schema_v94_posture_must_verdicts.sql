-- schema_v94 — posture_must_verdicts (single source of truth for per-MUST state)
--
-- Establishes a canonical per-MUST verdict table populated by the posture
-- engine on every load_posture() run. Every consumer (template renderer,
-- SPA leaf-detail, chat, dashboard) reads from here instead of each
-- re-running the engine or re-querying raw document_findings.
--
-- Grain: (tenant_id, must_id) unique. must_id shape: 'item:CTRL:slug'.
-- Refresh cadence: same as posture_controls — on upload + periodic sweep +
-- on-demand load_posture calls.
--
-- Phase 1 audit (2026-08-10) confirmed engine per-MUST output faithfully
-- represents recognised / partial / stale / N/A dimensions on 18-MUST
-- sample. This table persists that engine output.
--
-- Companion tables (parallel design):
--   posture_controls      — per-control cached verdict (Comply/OFI/NC)
--   posture_assertions    — per-control engine + tenant assertion audit log
--   tenant_evidence_gaps  — per-leaf gap tracking
--   posture_must_verdicts — this file: per-MUST truth (new)

CREATE TABLE IF NOT EXISTS posture_must_verdicts (
    id            bigserial   PRIMARY KEY,
    tenant_id     uuid        NOT NULL,
    must_id       text        NOT NULL,
    control_ref   text        NOT NULL,
    standard_id   text        NOT NULL,
    -- Verdict facets — engine emits three independent booleans:
    satisfied     boolean     NOT NULL,   -- all-recognised (present-status finding OR fresh cite)
    stale         boolean     NOT NULL DEFAULT FALSE,   -- recognised but past freshness_days
    partial       boolean     NOT NULL DEFAULT FALSE,   -- partial-only findings, no present
    -- Notes for auditor + debug (optional):
    reason        text,
    computed_at   timestamptz NOT NULL DEFAULT now(),

    -- One row per tenant per MUST — writer upserts.
    CONSTRAINT uq_pmv_tenant_must UNIQUE (tenant_id, must_id)
);

CREATE INDEX IF NOT EXISTS idx_pmv_tenant_control
    ON posture_must_verdicts (tenant_id, control_ref, standard_id);
CREATE INDEX IF NOT EXISTS idx_pmv_tenant_satisfied
    ON posture_must_verdicts (tenant_id) WHERE satisfied;

-- RLS tenant isolation (mirror of tenant_must_overrides + posture_controls)
ALTER TABLE posture_must_verdicts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pmv_tenant_isolation ON posture_must_verdicts;
CREATE POLICY pmv_tenant_isolation ON posture_must_verdicts
    USING      ((tenant_id)::text = current_setting('app.tenant_id', true))
    WITH CHECK ((tenant_id)::text = current_setting('app.tenant_id', true));

GRANT SELECT, INSERT, UPDATE, DELETE ON posture_must_verdicts TO arioncomply_app;
GRANT USAGE ON SEQUENCE posture_must_verdicts_id_seq TO arioncomply_app;
