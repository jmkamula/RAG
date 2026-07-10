-- schema_v62_signal_precision.sql
--
-- Signal-fusion Wave 4a (2026-07-09): precision feedback loop.
--
-- Adds `corroborating_signals text[]` to document_findings so the writer
-- stamps WHICH independent signals agreed at auto-approve time. Enables
-- rolling per-signal precision measurement (approved vs later-rejected
-- rates) that Wave 4a's read-side uses to weight signals dynamically.
--
-- Signal values recorded (matching posture_writer._write_document_findings):
--   'target_controls'   — doc_mappings filename+topic match
--   'semantic_controls' — musts_arioncomply top-K semantic match
--   'explicit_refs'     — regex-extracted control refs the doc self-cites
--   'llm_extracted'     — LLM produced any 'extracted' finding on this
--                         control in the same batch
--
-- Precision computation lives in application code (read-only query over
-- this column joined with review_status). No materialized view yet —
-- direct aggregation is fast at Arion's current volumes; a rollup view
-- can be added later if the gate's read-path becomes a bottleneck.

BEGIN;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS corroborating_signals text[] NOT NULL DEFAULT '{}';

COMMENT ON COLUMN document_findings.corroborating_signals IS
'Wave 4a: which independent corroboration signals agreed the control was in scope at write-time. Read together with review_status to compute rolling per-signal precision. Values: target_controls / semantic_controls / explicit_refs / llm_extracted.';

-- Partial index for precision lookups — only auto-approved fingerprint
-- matches with at least one corroborating signal contribute to the
-- precision calculation. Everything else (pending, non-fingerprint) is
-- irrelevant.
CREATE INDEX IF NOT EXISTS idx_document_findings_precision_lookup
    ON document_findings (tenant_id, standard_id, inference_source, review_status)
 WHERE inference_source = 'fingerprint_match'
   AND is_active = TRUE
   AND array_length(corroborating_signals, 1) > 0;

COMMIT;
