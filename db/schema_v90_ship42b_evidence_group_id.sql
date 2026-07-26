-- schema_v90 — Ship 42'.b — evidence_group_id column on document_findings.
--
-- Adds nullable dedup key stamped at INSERT by posture_writer.write_findings.
-- Rows sharing the same evidence_group_id are UI-collapsed to a single
-- auditor-facing citation but preserved individually for engine per-MUST
-- recognition (leaf_evaluators._fetch_recognised_items queries
-- checklist_item_id = ANY(...) unchanged).
--
-- Legacy rows have NULL evidence_group_id. Surface layer filters use
-- `WHERE evidence_group_id IS NULL OR rn=1` semantics to preserve legacy
-- visibility until backfill script runs.
--
-- Corresponding memory: [[ship-42-prime-a-dedup-design-2026-07-26]].

ALTER TABLE document_findings
  ADD COLUMN IF NOT EXISTS evidence_group_id text;

CREATE INDEX IF NOT EXISTS idx_document_findings_evidence_group
  ON document_findings (tenant_id, evidence_group_id)
  WHERE evidence_group_id IS NOT NULL;

COMMENT ON COLUMN document_findings.evidence_group_id IS
  'Ship 42 dedup key: sha1(document_id || control_ref || normalized_excerpt)[:16]. '
  'Rows sharing the same evidence_group_id are UI-collapsed to a single '
  'auditor-facing citation but preserved individually for engine per-MUST '
  'recognition. NULL for legacy rows (pre-Ship-42); backfill script populates.';
