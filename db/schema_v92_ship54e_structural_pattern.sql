-- schema_v92_ship54e_structural_pattern.sql
--
-- Ship 54'.e Phase 2 (2026-08-03) — adds `structural_pattern` as a
-- new inference_source lane + `structural` grounding_method.
--
-- Design: structural evidence detectors (rag/intake/structural_
-- evidence.py) recognize doc-control headers, revision-history
-- tables, signature blocks, interested-parties enumerations, and
-- tables of contents in uploaded documents. When present, they
-- produce document_findings bound to specific MUST items (e.g.,
-- doc-control 'Approved By' → item:5.2:approved with excerpt =
-- "Approved By: Maria Silva, CEO").
--
-- Companion to Ship 54'.d which emits the same shape at generation.
-- Closes the round-trip: our renderer emits <<DOC_CONTROL>> tables,
-- our extractor recognizes them on re-upload + auto-binds evidence.

BEGIN;

-- Add 'structural_pattern' to the allowed inference_source values.
ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_inference_source_check;

ALTER TABLE document_findings
    ADD  CONSTRAINT document_findings_inference_source_check
    CHECK (inference_source = ANY (ARRAY[
        'extracted',
        'xfw_bridge',
        'regex_explicit',
        'llm_xfw',
        'workbook',
        'leaf_scan',
        'form',
        'templated',
        'fingerprint_match',
        'structural_pattern'
    ]));

-- Add 'structural' to the allowed grounding_method values.
ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_grounding_method_check;

ALTER TABLE document_findings
    ADD  CONSTRAINT document_findings_grounding_method_check
    CHECK (grounding_method IS NULL OR grounding_method = ANY (ARRAY[
        'extractor_verbatim',
        'workbook',
        'template',
        'fingerprint',
        'leaf_scan',
        'manual',
        'form',
        'unknown',
        'structural'
    ]));

COMMIT;
