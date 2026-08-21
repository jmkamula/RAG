-- schema_v106_cite_hyperlink_display.sql
--
-- Ship 92'.d (2026-08-21) — humanize the cite attestation surface.
--
-- Ship 92'.a captured cite URLs; Ship 92'.c surfaced them on the
-- dashboard card. Tenant sees raw SharePoint tokenized URLs which
-- are unreadable ("../../..../:w:/r/sites/.../Doc.aspx?sourcedoc=%7B..."
-- when the cell's real display text is 'Information Security Policy').
--
-- Ship 85'.a's hyperlink capture already extracts both `url` and
-- `label`/`display` per cell — we just weren't storing the display
-- text on the cite row. This column adds it for tenant-facing
-- rendering, with fallback to URL basename or a `file=` query
-- param extract when display is empty (e.g. filename-only cells).

BEGIN;

ALTER TABLE external_evidence_source
    ADD COLUMN IF NOT EXISTS hyperlink_display TEXT;

COMMENT ON COLUMN external_evidence_source.hyperlink_display IS
  'Ship 92''.d — the cell display text captured alongside the '
  'hyperlink (openpyxl `Hyperlink.display` or the cell''s string '
  'value). Preferred for tenant-facing surfaces; the raw URL '
  'stays available in hyperlink_url for auditor drill-in. When '
  'multiple hyperlinks in the same cite column collapse to one '
  'cite row, this stores the FIRST non-empty display text.';

COMMIT;
