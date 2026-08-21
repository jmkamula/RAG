-- schema_v103_workbook_llm_arbiter.sql
--
-- Ship 91'.b (2026-08-20) — workbook LLM row-arbiter integration.
--
-- Ship 91'.a introduced `rag/intake/workbook_arbiter.py` — an LLM
-- pass that runs AFTER workbook_persistence structural extraction,
-- reads the catalog's three-way discipline (required / optional /
-- cite) as scaffolding, and emits per-row per-MUST findings the
-- structural pass missed. Precision safeguards: (a) MUST id
-- validated against Neo4j, (b) evidence_text substring-verified
-- against the LLM-claimed source cell.
--
-- This migration extends two CHECK allowlists so writes land clean:
--   document_findings.inference_source:  + workbook_llm_arbiter
--   document_findings.grounding_method:  + workbook_llm_arbiter
--
-- Ship 6'.b mapping (`rag/intake/posture_writer.py::_INFERENCE_TO_GROUNDING`)
-- keeps 1:1 correspondence between inference_source and
-- grounding_method (auditor telemetry — "how did this finding come
-- into being"). New pathway → new pair of allowlist values.

BEGIN;

-- ── 1. inference_source allowlist ──────────────────────────────────────

ALTER TABLE document_findings
  DROP CONSTRAINT IF EXISTS document_findings_inference_source_check;

ALTER TABLE document_findings
  ADD CONSTRAINT document_findings_inference_source_check
  CHECK (inference_source = ANY (ARRAY[
    'extracted',
    'xfw_bridge',
    'regex_explicit',
    'llm_xfw',
    'workbook',
    'workbook_llm_arbiter',    -- Ship 91'.b (2026-08-20)
    'leaf_scan',
    'form',
    'templated',
    'fingerprint_match',
    'structural_pattern'
  ]));

COMMENT ON COLUMN document_findings.inference_source IS
'How the finding was inferred. Ship 91'' added workbook_llm_arbiter '
'— LLM row-arbiter running after workbook_persistence structural '
'pass, reads catalog three-way discipline (required/optional/cite) '
'as scaffolding, emits per-row per-MUST findings the structural '
'pass missed. Verified via substring-match to source cell.';

-- ── 2. grounding_method allowlist ──────────────────────────────────────

ALTER TABLE document_findings
  DROP CONSTRAINT IF EXISTS document_findings_grounding_method_check;

ALTER TABLE document_findings
  ADD CONSTRAINT document_findings_grounding_method_check
  CHECK (grounding_method IS NULL OR grounding_method = ANY (ARRAY[
    'extractor_verbatim',
    'workbook',
    'workbook_llm_arbiter',    -- Ship 91'.b (2026-08-20)
    'template',
    'fingerprint',
    'leaf_scan',
    'manual',
    'form',
    'unknown',
    'structural'
  ]));

COMMENT ON COLUMN document_findings.grounding_method IS
'Ship 6''.b — auditor-facing pathway label for how evidence was '
'grounded. Ship 91''.b added workbook_llm_arbiter — LLM output '
'substring-verified against source cell content at claimed '
'(row, column) coordinates.';

COMMIT;
