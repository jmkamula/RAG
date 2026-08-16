-- Ship 74'.b (2026-08-16) — surface the canonical upload on duplicate
-- rows in intake_trace_log.
--
-- The pipeline already passes `dup_of_upload_id=_canonical` on the
-- `duplicate` stage (doc_pipeline.py:306) but the column never existed
-- and the tracer allowlist never accepted the kwarg. Silent-drop
-- squared. The Ship 74'.b allowlist guard caught this on first run.
--
-- Purpose: auditor-facing surface for "why did nothing happen on this
-- upload?" — the trace row now names the earlier upload whose
-- markdown/checksum matched, so operators can pivot to that record.
--
-- Nullable; only populated on `stage='duplicate'` rows.

BEGIN;

ALTER TABLE intake_trace_log
  ADD COLUMN dup_of_upload_id TEXT NULL;

COMMENT ON COLUMN intake_trace_log.dup_of_upload_id IS
  'Ship 74''.b — canonical upload_id whose content this upload duplicated. '
  'Populated only on duplicate-stage rows (markdown/checksum match).';

COMMIT;
