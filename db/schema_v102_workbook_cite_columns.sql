-- schema_v102_workbook_cite_columns.sql
--
-- Ship 89'.b (2026-08-20) — workbook cite-mode integration.
--
-- Ship 87'.a codified corroboration: "a cell that points at evidence
-- is not the same as a cell that contains it." Ship 88 (uncommitted)
-- tried to wire that as a new workbook_hyperlink_followup sibling
-- table — WRONG shape. Auditor semantics: a workbook row citing a
-- policy URL IS cited-mode evidence, and cite-mode already exists
-- (Ship 3'-arc external_evidence_source + verification_log +
-- cite_verification_overdue notification).
--
-- Ship 89'.b: workbook YAMLs get a new declarative field
-- (`cite_columns:`) alongside required_columns / optional_columns.
-- Cells in cite_columns emit rows into the EXISTING
-- external_evidence_source, tagged with the workbook row of origin.
--
-- Storage decision: reuse the existing table; add one FK column
-- (origin_finding_id) for auditor attribution back to the workbook
-- row that produced the cite.
--
-- Engine posture: unchanged. The workbook document_finding keeps its
-- YAML-declared status (present/partial per anchor/corroboration
-- rule). The cite adds an auditor-visible layer WITHOUT gating engine
-- verdict — matches the stored-vs-cited product principle: cited mode
-- is provenance, stored mode is evidence.
--
-- (Ship 88's uncommitted work — workbook_hyperlink_followup table,
-- has_hyperlink corroborating signal, workbook_link_resolver sweep,
-- workbook_link_unresolved notification kind — has been reverted;
-- this migration replaces the placeholder that would have shipped.)

BEGIN;

-- ── 1. origin_finding_id — attribution back to the workbook row ───────
--
-- Nullable because Ship 3' cite-mode had many origins pre-Ship 89'.b
-- (tenant profile, manual UI, tenant_external_system defaults). NULL
-- means "not from a workbook row — set manually or by another origin."

ALTER TABLE external_evidence_source
  ADD COLUMN IF NOT EXISTS origin_finding_id UUID
      REFERENCES document_findings(id) ON DELETE SET NULL;

COMMENT ON COLUMN external_evidence_source.origin_finding_id IS
  'Ship 89''.b (2026-08-20) — nullable FK to the workbook document_finding '
  'that produced this cite via a `cite_columns:` YAML binding. When NULL, '
  'the cite was created outside the workbook path (tenant profile UI, '
  'manual admin action, etc.). Auditor lens: "which workbook row cited '
  'this?" answers via this attribution.';

CREATE INDEX IF NOT EXISTS idx_external_evidence_source_origin_finding
  ON external_evidence_source (origin_finding_id)
  WHERE origin_finding_id IS NOT NULL;

COMMIT;
