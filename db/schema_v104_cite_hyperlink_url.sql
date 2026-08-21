-- schema_v104_cite_hyperlink_url.sql
--
-- Ship 92'.a.i (2026-08-21) — store the actual hyperlink URL on
-- external_evidence_source so the Ship 92'.a auto-verification
-- resolver can compare against uploaded documents.
--
-- Before: workbook_persistence emitted cite rows with `per_must_note`
-- (human-readable) but no machine-comparable URL. `origin_finding_id`
-- points at the workbook document_finding that produced the cite,
-- but the URL itself was discarded after the Ship 89'.b row-level
-- guard verified it.
--
-- After: hyperlink_url column stores the first non-mailto URL from
-- the matched cite column. Ship 92'.a.iii resolver compares basename
-- against client_documents.filename on doc upload to auto-verify.
--
-- Nullable — the 5 pre-existing cite rows (Ship 89'.b hand-picks
-- + Ship 90'.a sweep) don't have URL stored; new emissions do.
-- Backfill deferred (Ship 92'.b or later — requires re-extracting
-- the source workbooks).

BEGIN;

ALTER TABLE external_evidence_source
    ADD COLUMN IF NOT EXISTS hyperlink_url TEXT;

COMMENT ON COLUMN external_evidence_source.hyperlink_url IS
  'Ship 92''.a.i — the actual hyperlink URL captured from the matched '
  'workbook cite_columns cell. Used by Ship 92''.a.iii auto-verification '
  'resolver to compare against client_documents.filename on document '
  'upload. Nullable — pre-Ship-92 rows have no URL; new workbook_persistence '
  'emissions populate it. Multiple hyperlinks in the same cite column '
  'collapse to one cite via UNIQUE(tenant, must_id, system_id); this '
  'column stores the FIRST non-mailto URL discovered on the sheet.';

CREATE INDEX IF NOT EXISTS idx_external_evidence_source_url_active
    ON external_evidence_source (tenant_id, hyperlink_url)
    WHERE is_active = TRUE AND hyperlink_url IS NOT NULL;

COMMIT;
