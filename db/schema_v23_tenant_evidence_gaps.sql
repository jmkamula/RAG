-- =============================================================================
-- schema_v23_tenant_evidence_gaps.sql
--
-- Persistent per-leaf gap records emitted by the fulfilment engine, with
-- a client-side "acknowledge" path so HITL ownership of posture is honored.
--
-- One row per (tenant_id, control_id, leaf_id) — the leaf is the smallest
-- unit the engine reasons about. A control with N unsatisfied leaves
-- produces N rows on engine evaluation; satisfied leaves never appear.
--
-- Status lifecycle:
--   open         — engine reported the gap; client hasn't seen / actioned it
--   acknowledged — client confirms they're aware (with rationale); the gap
--                  is *suppressed from the headline gap list* but the verdict
--                  itself stays OFI/NC. Posture ownership stays with the
--                  client per [[human_in_the_loop_positioning]]: acknowledging
--                  ≠ deciding the control is Comply.
--   resolved     — engine no longer reports the gap on a subsequent run (the
--                  underlying leaf is now satisfied). Set by the engine
--                  writer, not by the client.
--
-- The unique (tenant_id, control_id, leaf_id) constraint lets the engine
-- UPSERT cleanly on each evaluation: existing acknowledgements survive
-- engine re-runs as long as the leaf still fails; once the leaf goes
-- satisfied, the row flips to resolved (acknowledged rationale preserved
-- in the audit trail).
--
-- Per [[sql_dry_run_nested_transaction]]: the COMMIT below makes this file
-- self-committing. Do not rely on an outer BEGIN/ROLLBACK to undo it.
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS tenant_evidence_gaps (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    control_id      text NOT NULL,                -- e.g. 'ISO27001:2022:A.5.1'
    control_ref     text NOT NULL,                -- e.g. 'A.5.1' (for joins / chat lookup)
    standard_id     text NOT NULL,                -- e.g. 'ISO27001:2022'
    leaf_id         text NOT NULL,                -- e.g. 'req:A.5.1:review_record'
    role            text NOT NULL,                -- e.g. 'review_record'
    evidence_type   text NOT NULL,                -- e.g. 'review_record'
    gap_summary     text NOT NULL,                -- auditor-style summary of what's missing
    gap_items       text[] NOT NULL DEFAULT '{}', -- the leaf's MUST items still missing
    status          text NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'acknowledged', 'resolved')),
    rationale       text,                         -- client's reason for acknowledging
    acknowledged_by text,                         -- user id / email
    acknowledged_at timestamptz,
    first_seen_at   timestamptz NOT NULL DEFAULT now(),
    last_seen_at    timestamptz NOT NULL DEFAULT now(),
    resolved_at     timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, control_id, leaf_id)
);

-- Primary read pattern: "show me the open gaps for control X"
CREATE INDEX IF NOT EXISTS idx_tenant_evidence_gaps_lookup
    ON tenant_evidence_gaps (tenant_id, control_id, status);

-- Secondary read: "what gaps did we acknowledge?" — supports the chat
-- surface listing of acknowledged items without a status-only scan.
CREATE INDEX IF NOT EXISTS idx_tenant_evidence_gaps_ack
    ON tenant_evidence_gaps (tenant_id, status, acknowledged_at DESC)
    WHERE status = 'acknowledged';

-- RLS — same pattern as posture_status_log: arioncomply_app gets the
-- constant-true policy and tenant scoping is enforced at the query layer
-- via set_config('app.tenant_id', ...). Superuser bypasses.
ALTER TABLE tenant_evidence_gaps ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_tenant_evidence_gaps ON tenant_evidence_gaps;
CREATE POLICY app_all_tenant_evidence_gaps ON tenant_evidence_gaps
    FOR ALL
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE ON tenant_evidence_gaps TO arioncomply_app;
-- No DELETE grant — gaps are part of the audit trail. Superuser can prune
-- for retention if needed.

COMMIT;
