-- schema_v33 — exclude 'failed' from the document_uploads dedup predicate.
--
-- Before: the unique index on (tenant_id, sha256) only excluded rows with
-- extraction_status='duplicate'. A pipeline crash leaving a row at
-- extraction_status='failed' would then block all re-uploads of the same
-- file — even though the failed attempt produced no findings and the bug
-- causing the crash had been fixed.
--
-- After: 'failed' rows are kept (audit log) but don't block re-uploads of
-- the same SHA256. The application-side dedup query in
-- api_server.py:upload_document mirrors this predicate.
--
-- Surfaced 2026-06-09 by Information Security and Data Management
-- Process.docx — first upload failed via ModuleNotFoundError in
-- _merge_small_sections (fixed in commit 6a564a7); the re-upload was
-- rejected as a duplicate of the failed row.

BEGIN;

DROP INDEX IF EXISTS uniq_document_uploads_tenant_sha256;
CREATE UNIQUE INDEX uniq_document_uploads_tenant_sha256
    ON public.document_uploads (tenant_id, sha256)
    WHERE sha256 IS NOT NULL
      AND extraction_status NOT IN ('duplicate', 'failed');

DROP INDEX IF EXISTS idx_doc_uploads_tenant_filename_nodup;
CREATE INDEX idx_doc_uploads_tenant_filename_nodup
    ON public.document_uploads (tenant_id, filename)
    WHERE extraction_status NOT IN ('duplicate', 'failed');

COMMIT;
