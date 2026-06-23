-- schema_v44 — workbook sheet classification telemetry.
--
-- Part A of the workbook intake architectural cleanup (see
-- [[workbook-importer-bare-annex-a-2026-06-23]]). _extract_structured
-- retired for xlsx/xlsm; workbook_persistence (Stage 4.6) becomes the
-- canonical path. Sheets without a YAML mapping in
-- db/workbook_mappings/ produce 0 findings instead of unbound noise.
--
-- These columns surface the YAML-curation gap so operators can prioritise
-- Part B (extending workbook_mappings coverage):
--
--   workbook_sheets_total    — total content sheets (post meta-skip)
--   workbook_sheets_mapped   — sheets with a matching YAML
--   workbook_sheets_unmapped — sheets needing a new YAML
--   workbook_unmapped_sheets — comma-separated names of unmapped sheets
--   workbook_skipped_meta_sheets — comma-separated names of meta sheets
--                                  filtered by _read_xlsx blacklist
--
-- Future: dashboard quality flag goes yellow when workbook_sheets_unmapped
-- > 0 (telemetry says "you have an unmapped sheet; future tenants with
-- the same shape will hit this gap too").

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS workbook_sheets_total        INTEGER,
    ADD COLUMN IF NOT EXISTS workbook_sheets_mapped       INTEGER,
    ADD COLUMN IF NOT EXISTS workbook_sheets_unmapped     INTEGER,
    ADD COLUMN IF NOT EXISTS workbook_unmapped_sheets     TEXT,
    ADD COLUMN IF NOT EXISTS workbook_skipped_meta_sheets TEXT;
