-- schema_v54_fact_scope.sql — S3c cascade UPDATES_FACT + EXPANDS_SCOPE
--
-- Two additions to the cascade output:
--
-- 1. client_fact_change_log — append-only audit of every cascade-fired
--    ClientFact mutation. The existing `client_facts` table holds the
--    CURRENT per-tenant state (boolean column per fact); this log
--    captures the HISTORY of changes with provenance back to the
--    source verification.
--
-- 2. triggered_implication.scope_kind — optional column populated when
--    an implication was fired from an EXPANDS_SCOPE edge. Allows the
--    UI to render "this control's re-evaluation was triggered by a
--    new site, jurisdiction, etc.".

BEGIN;

-- ── client_fact_change_log ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS client_fact_change_log (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    fact_id                TEXT         NOT NULL,
    -- e.g. 'fact:employee_count_250_plus'

    operation              TEXT         NOT NULL,
    -- 'set' | 'clear' | 'recompute'

    old_value              BOOLEAN,
    -- NULL for 'recompute' (we don't read the column) or if the fact
    -- column didn't previously exist.

    new_value              BOOLEAN,
    -- Set for 'set'/'clear'; NULL for 'recompute' (observational only).

    applied                BOOLEAN      NOT NULL DEFAULT TRUE,
    -- FALSE for 'recompute' v1 — logged but not applied (column
    -- remains at whatever client_facts had). Set TRUE once recompute
    -- semantics are wired in S3d.

    source_verification_id UUID         NOT NULL
        REFERENCES external_evidence_verification_log(id) ON DELETE CASCADE,
    source_event_type      TEXT         NOT NULL,
    rationale              TEXT,

    fired_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT client_fact_change_log_operation_chk
        CHECK (operation IN ('set', 'clear', 'recompute'))
);

CREATE INDEX IF NOT EXISTS idx_client_fact_change_log_tenant_fired
    ON client_fact_change_log(tenant_id, fired_at DESC);

CREATE INDEX IF NOT EXISTS idx_client_fact_change_log_fact
    ON client_fact_change_log(tenant_id, fact_id, fired_at DESC);

ALTER TABLE client_fact_change_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON client_fact_change_log;
CREATE POLICY tenant_isolation ON client_fact_change_log
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

-- Append-only: no UPDATE / DELETE grant. SELECT for read; INSERT
-- exclusively via the cascade engine.
GRANT SELECT, INSERT ON client_fact_change_log TO arioncomply_app;

COMMENT ON TABLE client_fact_change_log IS
    'Append-only audit of ClientFact mutations from cascade UPDATES_FACT edges. Captures who/when/why and the resulting state.';


-- ── triggered_implication.scope_kind ──────────────────────────────────────
ALTER TABLE triggered_implication
    ADD COLUMN IF NOT EXISTS scope_kind TEXT;
-- Populated when this implication was fired from an EXPANDS_SCOPE edge.
-- Values: 'site' | 'jurisdiction' | 'supplier' | 'processing_activity'.
-- NULL for normal cascade implications.

COMMENT ON COLUMN triggered_implication.scope_kind IS
    'Set when the implication was fired by an EXPANDS_SCOPE edge (e.g. facility_added). Identifies which scope dimension expanded so the UI can render "re-evaluate for new site".';

COMMIT;
