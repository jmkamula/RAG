-- schema_v61_fingerprint_match_inference_source.sql
--
-- Adds 'fingerprint_match' to document_findings.inference_source
-- CHECK constraint. Enables the LLM-free intake pipeline (stage 4-5,
-- 2026-07-06): findings produced by the deterministic fingerprint
-- classifier + sentence-heuristic quote extractor, without any LLM
-- call. Complements existing sources:
--
--   'extracted'      — LLM extraction (default)
--   'xfw_bridge'     — cross-framework bridge proposal
--   'regex_explicit' — explicit ref regex from doc text
--   'llm_xfw'        — LLM-assisted cross-framework
--   'workbook'       — workbook YAML persistence
--   'leaf_scan'      — post-hoc catalog back-bind
--   'form'           — retired web-fill lane
--   'templated'      — MUST-marker fast-path (auto-approved)
--   'fingerprint_match' — NEW: deterministic classifier + quote

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
        'templated'::text,
        'fingerprint_match'::text
    ]));

COMMIT;
