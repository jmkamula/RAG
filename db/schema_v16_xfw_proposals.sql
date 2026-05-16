-- =============================================================================
-- schema_v16_xfw_proposals.sql
--
-- Surface cross-framework proposals in document_findings for HITL review.
--
-- 1. Add inferred_from_control_ref + inferred_from_standard_id so a reviewer
--    seeing a pending GDPR Art.32 finding can see "inferred from your A.5.18
--    finding via the IMPLEMENTS bridge".
-- 2. Add inference_source to distinguish proposals from confirmed findings.
--    Values: 'extracted' (default — direct from doc text), 'xfw_bridge'
--    (mirrored from a source finding via Neo4j IMPLEMENTS), 'regex_explicit'
--    (reserved for v2: detected by explicit_refs regex), 'llm_xfw' (reserved
--    for v2: second LLM pass).
-- 3. Add index on (tenant_id, inference_source) WHERE confirmed_by IS NULL
--    so the chat surface ("pending xfw proposals") is O(matching) not
--    O(all_findings).
--
-- Idempotence note: NO unique constraint on (tenant_id, document_id,
-- control_ref, standard_id). document_findings already has 14 duplicate rows
-- on that key, predating this migration. The xfw_proposer module handles
-- idempotence via delete-then-insert scoped to inference_source='xfw_bridge'
-- AND confirmed_by IS NULL — confirmed proposals are preserved across re-runs.
-- =============================================================================

BEGIN;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS inferred_from_control_ref text,
    ADD COLUMN IF NOT EXISTS inferred_from_standard_id text,
    ADD COLUMN IF NOT EXISTS inference_source          text
        NOT NULL DEFAULT 'extracted';

ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_inference_source_check;

ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_inference_source_check
    CHECK (inference_source = ANY (ARRAY[
        'extracted'::text,
        'xfw_bridge'::text,
        'regex_explicit'::text,
        'llm_xfw'::text
    ]));

-- Partial index for "pending xfw proposals" lookups — the chat surface
-- runs SELECT ... WHERE tenant_id=? AND inference_source='xfw_bridge'
-- AND confirmed_by IS NULL ORDER BY extracted_at DESC.
CREATE INDEX IF NOT EXISTS idx_doc_findings_pending_xfw
    ON document_findings (tenant_id, extracted_at DESC)
    WHERE confirmed_by IS NULL AND inference_source <> 'extracted';

COMMENT ON COLUMN document_findings.inferred_from_control_ref IS
    'For xfw_bridge proposals: the source control_ref this finding mirrors. '
    'NULL for extracted findings.';
COMMENT ON COLUMN document_findings.inferred_from_standard_id IS
    'For xfw_bridge proposals: the source standard_id this finding mirrors. '
    'NULL for extracted findings.';
COMMENT ON COLUMN document_findings.inference_source IS
    'How this row was produced: extracted (direct from doc text), '
    'xfw_bridge (mirrored via Neo4j IMPLEMENTS edge), '
    'regex_explicit (v2: regex-matched ref), llm_xfw (v2: second LLM pass).';

COMMIT;
