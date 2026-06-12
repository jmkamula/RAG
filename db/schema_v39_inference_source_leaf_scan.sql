-- schema_v39: extend document_findings.inference_source CHECK constraint
-- to allow the new 'leaf_scan' value.
--
-- Introduced by rag/intake/leaf_driven_scan.py (2026-06-12) — back-binds
-- existing approved findings to specific MUSTs they semantically satisfy
-- but weren't tagged with at extraction time. Proposals persist as new
-- document_findings rows with inference_source='leaf_scan' so they're
-- distinguishable from extracted / workbook / xfw_bridge findings in
-- Stage-1 review.

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
        'leaf_scan'::text
    ]));

COMMIT;
