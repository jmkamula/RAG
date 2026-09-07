-- schema_v117_pii_redaction_marker.sql
--
-- Ship 126'.b — marker migration.
--
-- Ship 126'.b enabled PII redaction at the WRITE path for three
-- log tables:
--
--   * ai_call_log.prompt_preview  + response_preview  (rag/ai_trace.py::_preview)
--   * chat_consensus_log.query                        (rag/consensus/log.py::log_consensus)
--   * chat_casefile_log.query + answer_text           (rag/casefile/log.py::log_casefile)
--
-- All new inserts pass through `rag/posture/pii_redactor.py::redact_pii()`
-- at default level (email / phone / SSN / credit card / IBAN / IPv4 /
-- national IDs — CZ + UK + FR). Names deliberately not redacted (matches
-- Auditor's Ledger policy — named accountability is load-bearing).
--
-- **Existing rows are backfilled by scripts/ops/backfill_pii_redaction.py**
-- (called by scripts/ops/ship-126-poc-update.sh). The Python backfill
-- runs the SAME redactor the write path uses — no SQL-regex approximation.
--
-- This migration is a marker only — it records the redaction discipline
-- start date in a comment for auditor traceability. No table changes.

BEGIN;

COMMENT ON COLUMN public.ai_call_log.prompt_preview IS
'Diagnostic 500-char preview of the LLM prompt. Ship 126''.b: PII scrubbed via pii_redactor.redact_pii() before persist (email/phone/SSN/CC/IBAN/IPv4/national-IDs). Names retained (compliance load-bearing). Historical rows backfilled by scripts/ops/backfill_pii_redaction.py.';

COMMENT ON COLUMN public.ai_call_log.response_preview IS
'Diagnostic 500-char preview of the LLM response. Ship 126''.b: PII scrubbed via pii_redactor.redact_pii() before persist. Same policy as prompt_preview.';

COMMENT ON COLUMN public.chat_consensus_log.query IS
'User query text (Ship 1 consensus). Ship 126''.b: PII scrubbed via pii_redactor.redact_pii() before persist. Diagnostic value (question shape, ref choice) retained; sensitive substrings become <email-redacted> / <phone-redacted> / etc.';

COMMENT ON COLUMN public.chat_casefile_log.query IS
'User query text (Ship 2'' case-file digest). Ship 126''.b: PII scrubbed via pii_redactor.redact_pii() before persist.';

COMMENT ON COLUMN public.chat_casefile_log.answer_text IS
'LLM answer text (Ship 6''.d claim scan). Ship 126''.b: PII scrubbed via pii_redactor.redact_pii() before persist. Answer text may echo query PII or tenant profile fields.';

COMMIT;
