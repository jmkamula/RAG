-- schema_v40: extend document_findings.inference_source CHECK constraint
-- to allow the new 'form' value.
--
-- Introduced by the per-MUST advisory form (2026-06-15) — tenant fills
-- evidence per MUST in the dashboard "How to advance" panel; each filled
-- field becomes a document_findings row with checklist_item_id set and
-- inference_source='form' so it's distinguishable from extractor /
-- workbook / leaf-scan rows.

BEGIN;

ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_inference_source_check;

ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_inference_source_check
    CHECK (inference_source = ANY (ARRAY[
        'extracted'::text,
        'xfw_bridge'::text,
        'regex_explicit'::text,
        'llm_xfw'::text,
        'workbook'::text,
        'leaf_scan'::text,
        'form'::text
    ]));

COMMIT;
