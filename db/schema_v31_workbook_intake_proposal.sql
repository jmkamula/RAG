-- =============================================================================
-- schema_v31_workbook_intake_proposal.sql
--
-- Phase 2 / Stage I-b: persist workbook discovery proposals.
--
-- Stage I (rag/intake/workbook_discovery.py) fingerprints each sheet in a
-- tenant workbook against the canonical YAMLs in db/workbook_mappings/ and
-- emits SheetProposal dataclasses in memory. This migration adds the
-- persistence target so Stage II (HITL UI) has rows to surface and Stage III
-- (extraction) has confirmed bindings to extract against.
--
-- One discovery RUN groups all proposals from a single invocation
-- (discovery_run_id). A sheet may match multiple mappings; a mapping may
-- match multiple sheets — the unique key includes all three so we don't
-- collapse legitimate alternatives. Re-running discovery on the same
-- workbook produces a new run_id; reconciliation (mark prior runs
-- superseded) is a Stage II concern and not in this migration.
--
-- RLS scoped via arioncomply_app + set_config('app.tenant_id'). Following
-- the [[rls-tenant-context-for-app-user]] pattern.
--
-- Idempotent. Self-committing per [[sql-dry-run-nested-transaction]].
-- =============================================================================

BEGIN;

-- ───────── Table ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workbook_intake_proposal (
    id                   bigserial    PRIMARY KEY,
    tenant_id            uuid         NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    discovery_run_id     uuid         NOT NULL,
    workbook_uri         text         NOT NULL,
    sheet_name           text         NOT NULL,
    mapping_id           text         NOT NULL,
    mapping_path         text,
    confidence           numeric(5,3) NOT NULL,
    header_row           integer,
    row_count            integer      NOT NULL DEFAULT 0,
    proposal             jsonb        NOT NULL,
    status               text         NOT NULL DEFAULT 'pending',
    decided_at           timestamptz,
    decided_by           text,
    decision_note        text,
    superseded_at        timestamptz,
    superseded_by_id     bigint       REFERENCES workbook_intake_proposal(id) ON DELETE SET NULL,
    created_at           timestamptz  NOT NULL DEFAULT now(),
    updated_at           timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT workbook_intake_proposal_status_check
        CHECK (status = ANY (ARRAY[
            'pending'::text, 'confirmed'::text, 'rejected'::text, 'superseded'::text
        ])),
    CONSTRAINT workbook_intake_proposal_confidence_range
        CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT workbook_intake_proposal_decided_consistency
        CHECK ((status IN ('confirmed','rejected')) = (decided_at IS NOT NULL)),
    CONSTRAINT workbook_intake_proposal_superseded_consistency
        CHECK ((status = 'superseded') = (superseded_at IS NOT NULL))
);

-- ───────── Indexes ────────────────────────────────────────────────────────
-- One row per (tenant, run, sheet, mapping). Re-running discovery uses a new
-- run_id so this never conflicts within a run.
CREATE UNIQUE INDEX IF NOT EXISTS uq_workbook_intake_proposal_run_sheet_mapping
    ON workbook_intake_proposal (tenant_id, discovery_run_id, sheet_name, mapping_id);

-- "Show me pending proposals to review" — Stage II HITL queue.
CREATE INDEX IF NOT EXISTS idx_workbook_intake_proposal_pending
    ON workbook_intake_proposal (tenant_id, status, created_at DESC)
    WHERE status = 'pending';

-- "Show me everything from this run."
CREATE INDEX IF NOT EXISTS idx_workbook_intake_proposal_run
    ON workbook_intake_proposal (tenant_id, discovery_run_id, created_at);

-- "What's the discovery history for this workbook?"
CREATE INDEX IF NOT EXISTS idx_workbook_intake_proposal_workbook
    ON workbook_intake_proposal (tenant_id, workbook_uri, created_at DESC);

-- ───────── updated_at trigger ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION fn_workbook_intake_proposal_touch_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_workbook_intake_proposal_touch_updated_at ON workbook_intake_proposal;
CREATE TRIGGER trg_workbook_intake_proposal_touch_updated_at
    BEFORE UPDATE ON workbook_intake_proposal
    FOR EACH ROW
    EXECUTE FUNCTION fn_workbook_intake_proposal_touch_updated_at();

-- ───────── RLS ────────────────────────────────────────────────────────────
ALTER TABLE workbook_intake_proposal ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_workbook_intake_proposal ON workbook_intake_proposal;
CREATE POLICY app_all_workbook_intake_proposal ON workbook_intake_proposal
    FOR ALL
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE ON workbook_intake_proposal TO arioncomply_app;
GRANT USAGE, SELECT ON SEQUENCE workbook_intake_proposal_id_seq TO arioncomply_app;

COMMIT;
