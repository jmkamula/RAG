-- schema_v46: extend document_findings.inference_source CHECK to allow
-- the new 'templated' value.
--
-- Introduced by the templated-upload fast path (2026-06-24) — when a
-- tenant uploads a doc derived from one of our template scaffolds
-- (markdown with <<MUST item:X>> markers), the extractor binds
-- deterministically without an LLM call. Per-MUST findings written
-- with inference_source='templated' are distinguishable from
-- LLM-extracted ('extracted'), workbook-extracted ('workbook'),
-- form-authored ('form'), etc.

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
        'form'::text,
        'templated'::text
    ]));

COMMIT;
