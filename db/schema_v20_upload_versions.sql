-- =============================================================================
-- schema_v20_upload_versions.sql
--
-- Date-versioned uploads. When the same filename is uploaded again (with
-- different content — byte-identical re-uploads are still rejected by the
-- v19 dedup), the new row joins the existing series as the next version.
--
-- Series semantics:
--   • A "series" is a tenant-scoped sequence of uploads sharing the same
--     filename. Members are non-duplicate document_uploads rows.
--   • series_id is stable across versions; version_no starts at 1 and
--     increments by 1.
--   • Duplicates (extraction_status='duplicate') do NOT join the series —
--     they are tombstones with dup_of_upload_id pointing at the canonical
--     row that does hold the series membership.
--
-- The upload endpoint computes (series_id, version_no) at INSERT time by
-- looking up the existing series for (tenant_id, filename); a NULL series_id
-- on a non-duplicate row is a bug.
-- =============================================================================

BEGIN;

-- ── Columns ────────────────────────────────────────────────────────────────
ALTER TABLE document_uploads
    ADD COLUMN IF NOT EXISTS series_id  uuid,
    ADD COLUMN IF NOT EXISTS version_no integer;

-- ── Backfill: assign series_id + version_no to existing non-duplicate rows.
-- One series per (tenant_id, filename), version_no by uploaded_at then id.
-- Idempotent: skip rows that already have series_id populated.
WITH groups AS (
    SELECT tenant_id, filename, gen_random_uuid() AS new_series_id
      FROM document_uploads
     WHERE extraction_status <> 'duplicate'
       AND series_id IS NULL
     GROUP BY tenant_id, filename
),
numbered AS (
    SELECT u.id,
           g.new_series_id                                            AS series_id,
           ROW_NUMBER() OVER (
               PARTITION BY u.tenant_id, u.filename
               ORDER BY u.uploaded_at, u.id
           )                                                          AS version_no
      FROM document_uploads u
      JOIN groups          g
        ON g.tenant_id = u.tenant_id
       AND g.filename  = u.filename
     WHERE u.extraction_status <> 'duplicate'
       AND u.series_id IS NULL
)
UPDATE document_uploads u
   SET series_id  = n.series_id,
       version_no = n.version_no
  FROM numbered n
 WHERE u.id = n.id;

-- ── Constraints ────────────────────────────────────────────────────────────
-- Both columns must be set together (or both NULL for legacy/duplicate rows).
ALTER TABLE document_uploads
    DROP CONSTRAINT IF EXISTS document_uploads_series_version_paired;

ALTER TABLE document_uploads
    ADD CONSTRAINT document_uploads_series_version_paired
    CHECK (
        (series_id IS NULL AND version_no IS NULL)
        OR
        (series_id IS NOT NULL AND version_no IS NOT NULL AND version_no >= 1)
    );

-- ── Indexes ────────────────────────────────────────────────────────────────
-- Uniqueness: (series_id, version_no) — version_no is per-series, so we
-- don't need tenant_id in the key (series_id is already tenant-scoped by
-- construction).
CREATE UNIQUE INDEX IF NOT EXISTS uniq_document_uploads_series_version
    ON document_uploads (series_id, version_no)
    WHERE series_id IS NOT NULL;

-- Fast "what series is this filename in?" lookup on the upload path.
CREATE INDEX IF NOT EXISTS idx_doc_uploads_tenant_filename_nodup
    ON document_uploads (tenant_id, filename)
    WHERE extraction_status <> 'duplicate';

-- Fast "list versions of this series" lookup on the read endpoint.
CREATE INDEX IF NOT EXISTS idx_doc_uploads_series
    ON document_uploads (series_id, version_no)
    WHERE series_id IS NOT NULL;

COMMIT;
