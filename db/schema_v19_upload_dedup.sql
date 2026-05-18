-- =============================================================================
-- schema_v19_upload_dedup.sql
--
-- Make uploads idempotent — same content uploaded twice never produces a
-- second set of findings.
--
-- Two layers of dedup, each with its own unique constraint:
--
--   1. Source bytes (document_uploads.sha256, set in the upload endpoint
--      before the file is even written to disk). Catches the common case:
--      user re-clicks "upload" on the same file.
--
--   2. Normalized markdown (document_text.markdown_sha256, set after
--      Stage 1 parses the file). Catches the harder case: same content,
--      different export (DOCX vs PDF) so the byte hashes differ but the
--      LLM input is identical.
--
-- Duplicates aren't silently dropped — the second attempt is recorded with
-- extraction_status='duplicate' and a dup_of_upload_id pointer back to the
-- canonical row. That way:
--   • the status endpoint can answer for the rejected upload_id
--   • the unique constraint isn't violated by the tombstone (partial index)
--   • audit can see "user X tried to re-upload at time T2"
-- =============================================================================

BEGIN;

-- ── extraction_status: allow the new 'duplicate' value ─────────────────────
-- The CHECK is named implicitly by Postgres as <table>_<column>_check.
ALTER TABLE document_uploads
    DROP CONSTRAINT IF EXISTS document_uploads_extraction_status_check;

ALTER TABLE document_uploads
    ADD CONSTRAINT document_uploads_extraction_status_check
    CHECK (extraction_status IN (
        'pending',
        'processing',
        'completed',
        'failed',
        'manual_review',
        'duplicate'
    ));

-- ── dup_of_upload_id: pointer back to the canonical upload ─────────────────
ALTER TABLE document_uploads
    ADD COLUMN IF NOT EXISTS dup_of_upload_id uuid
        REFERENCES document_uploads(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_doc_uploads_dup_of
    ON document_uploads (dup_of_upload_id)
    WHERE dup_of_upload_id IS NOT NULL;

-- ── Backfill: pre-v19 test fixtures sometimes wrote placeholder sha256
-- values ('test-fixture' literal) across multiple rows. Mark the newer
-- collision rows as duplicates of the oldest sibling so the unique
-- index can be built. The corresponding document_text row is dropped
-- because document_text's PK is upload_id and we keep only the
-- canonical one. Idempotent — re-running this skips rows already
-- marked 'duplicate'.
WITH ranked AS (
    SELECT id,
           ROW_NUMBER() OVER (
               PARTITION BY tenant_id, sha256
               ORDER BY uploaded_at, id
           )                                                AS rn,
           FIRST_VALUE(id) OVER (
               PARTITION BY tenant_id, sha256
               ORDER BY uploaded_at, id
           )                                                AS keeper
      FROM document_uploads
     WHERE sha256 IS NOT NULL
       AND extraction_status <> 'duplicate'
)
UPDATE document_uploads u
   SET extraction_status = 'duplicate',
       dup_of_upload_id  = r.keeper
  FROM ranked r
 WHERE u.id = r.id
   AND r.rn > 1;

DELETE FROM document_text
 WHERE upload_id IN (
    SELECT id FROM document_uploads WHERE extraction_status = 'duplicate'
 );

-- ── Layer 1: source-byte dedup (tenant_id, sha256) ─────────────────────────
-- Partial index: only enforce uniqueness on non-NULL sha256 (older rows
-- pre-v18 may not have it) and only across non-duplicate rows (so the
-- tombstones we write don't collide with the canonical).
CREATE UNIQUE INDEX IF NOT EXISTS uniq_document_uploads_tenant_sha256
    ON document_uploads (tenant_id, sha256)
    WHERE sha256 IS NOT NULL
      AND extraction_status <> 'duplicate';

-- ── Layer 2: markdown-content dedup (tenant_id, markdown_sha256) ───────────
-- The intake pipeline pre-checks before inserting document_text, so the
-- constraint is mostly a safety net against races and direct writes.
CREATE UNIQUE INDEX IF NOT EXISTS uniq_document_text_tenant_markdown_sha256
    ON document_text (tenant_id, markdown_sha256);

COMMIT;
