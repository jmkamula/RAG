-- schema_v81_ship6b_grounding_method.sql
--
-- Ship 6'.b (2026-07-18) — first fix from the Ship 6'.a LLM-role audit.
--
-- Adds `document_findings.grounding_method` so auditors can see
-- per-finding evidence provenance. The extractor already runs a
-- `_evidence_grounded()` verbatim-substring check that drops
-- LLM-invented quotes before they reach the DB (see
-- rag/intake/extractor.py:385 and :2151). But once a finding is
-- persisted, we lose the record of WHICH safeguard it passed
-- through.
--
-- Values:
--   extractor_verbatim  — LLM extractor; excerpt substring-verified
--                         against doc.full_text or doc.markdown
--   workbook            — workbook_persistence YAML matcher; excerpt
--                         is the row's semantic value
--   template            — templated document with <<MUST item:X>>
--                         markers (deterministic fast path)
--   fingerprint         — fingerprint_match auto-approve; corroborated
--                         by ≥2 signals
--   leaf_scan           — leaf-driven back-bind (rare, HITL-only)
--   manual              — tenant added directly via UI / API
--   form                — retired 2026-07-04 web form path
--   unknown             — pre-Ship 6'.b rows, backfill or diagnostic
--
-- Nullable to allow backfill; new writes required to set explicitly.
-- CHECK constraint enforces the allowlist.

BEGIN;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS grounding_method text;

ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_grounding_method_check;
ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_grounding_method_check
    CHECK (
        grounding_method IS NULL OR grounding_method = ANY (ARRAY[
            'extractor_verbatim',
            'workbook',
            'template',
            'fingerprint',
            'leaf_scan',
            'manual',
            'form',
            'unknown'
        ])
    );

COMMENT ON COLUMN document_findings.grounding_method IS
'Ship 6''.b: how this finding''s evidence was verified. Auditor-facing provenance for the anti-hallucination safeguards described in [[ship-6-prime-a-llm-role-audit-2026-07-18]].';

-- Backfill from inference_source. This is a best-effort mapping:
-- rows written before Ship 6'.b didn't record the method, but
-- inference_source is a near-1:1 proxy.
UPDATE document_findings
   SET grounding_method = CASE
       WHEN inference_source = 'extracted'         THEN 'extractor_verbatim'
       WHEN inference_source = 'workbook'          THEN 'workbook'
       WHEN inference_source = 'templated'         THEN 'template'
       WHEN inference_source = 'fingerprint_match' THEN 'fingerprint'
       WHEN inference_source = 'leaf_scan'         THEN 'leaf_scan'
       WHEN inference_source = 'form'              THEN 'form'
       WHEN inference_source = 'xfw_bridge'        THEN 'unknown'   -- xfw is not evidence itself
       ELSE 'unknown'
   END
 WHERE grounding_method IS NULL;

-- Small performance index — auditors will query by method
CREATE INDEX IF NOT EXISTS idx_document_findings_grounding_method
    ON document_findings(tenant_id, grounding_method);

COMMIT;
