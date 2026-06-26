-- schema_v47: tabular_evidence_rows — per-row capture for tabular templates
--
-- The templated upload fast-path used to bind one finding per column
-- (extractor sample_cell[i] = first non-empty cell) for satisfaction
-- checking. That throws away every row after the first: a 50-row
-- asset register collapses to one finding per column = up to 6 rows
-- of evidence stored, but actual content of the other 49 register
-- rows is lost.
--
-- This table captures the FULL tabular content alongside the per-MUST
-- findings. The findings keep their semantics (engine asks "is this
-- column covered, yes/no?"); this table is the *content* the tenant
-- typed, kept verbatim so:
--   1. Renderer can replay all rows on round-trip (continuity across
--      annual refresh — tenant sees their 50 assets back, not 1).
--   2. Future advisory checks can surface per-row completeness
--      ("3 assets missing owner — rows 12, 19, 34").
--   3. Auditor view can sample rows for inspection.
--
-- One row per (document_id, leaf_id, row_index). row_index is 0-based
-- after stripping header + separator rows. column_values is JSONB of
-- {item_id: cell_text} — sparse (only non-empty cells included).
--
-- Authored 2026-06-26 — part of Phase 1 (capture). Phase 2 (engine
-- surface for completeness advisory) layers on later.

BEGIN;

CREATE TABLE IF NOT EXISTS tabular_evidence_rows (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id      UUID         NOT NULL,
    document_id    UUID         NOT NULL REFERENCES client_documents(id) ON DELETE CASCADE,
    leaf_id        TEXT         NOT NULL,
    -- e.g. 'req:A.5.9:asset_inventory'

    row_index      INTEGER      NOT NULL,
    -- 0-based, after header + separator stripped. Stable within a
    -- single document_id but not across documents.

    column_values  JSONB        NOT NULL DEFAULT '{}'::jsonb,
    -- Sparse map: {item_id: cell_text}. Empty cells omitted entirely
    -- (vs. set to empty string) so completeness checks can use
    -- presence-of-key semantics.

    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    -- Soft-delete; supersession sweeps on re-extract use this.

    extracted_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT tabular_evidence_rows_row_index_nonneg CHECK (row_index >= 0),
    CONSTRAINT tabular_evidence_rows_unique_per_doc UNIQUE (document_id, leaf_id, row_index)
);

CREATE INDEX IF NOT EXISTS idx_tabular_evidence_tenant_leaf
    ON tabular_evidence_rows(tenant_id, leaf_id) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_tabular_evidence_doc
    ON tabular_evidence_rows(document_id) WHERE is_active = TRUE;

-- RLS: same pattern as document_findings — app role sees only its
-- tenant's rows; superuser bypasses for backfills.
ALTER TABLE tabular_evidence_rows ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON tabular_evidence_rows;
CREATE POLICY tenant_isolation ON tabular_evidence_rows
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE, DELETE ON tabular_evidence_rows TO arioncomply_app;

COMMENT ON TABLE tabular_evidence_rows IS
    'Per-row capture of tabular template content. Sibling to document_findings; engine semantics unchanged.';
COMMENT ON COLUMN tabular_evidence_rows.column_values IS
    'Sparse JSONB map: {item_id: cell_text}. Empty cells omitted (not "").';

COMMIT;
