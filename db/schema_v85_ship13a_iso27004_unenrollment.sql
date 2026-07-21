-- schema_v85_ship13a_iso27004_unenrollment.sql
--
-- Ship 13'.a (2026-07-21) — unenroll ISO 27004.
--
-- Ship 12'.b (schema_v84) enrolled `ISO27004:2016`. Ship 13'.a
-- discovered the source PDF available for curation is the 2009
-- first edition, not the 2016 second edition. The two editions
-- restructured substantially — citing 2009 § pointers with a
-- 2016 badge risks auditor confusion.
--
-- Decision: unenroll 27004 entirely rather than curate against
-- the wrong edition. If/when the 2016 second edition text lands,
-- re-enroll then. The 7 monitoring leaves lose their `[Related
-- guidance: …]` footer content in this arc (see Ship 13'.a's
-- backfill scrub script).
--
-- Verification (run manually):
--   SELECT id, short_name, role FROM standards ORDER BY id;
-- Expected: 27004 absent. Guidance rows = ISO27002:2022 +
-- ISO27003:2017 + ISO27005:2022 only.

BEGIN;

DELETE FROM standards WHERE id = 'ISO27004:2016';

-- Sanity: no dependent rows should have referenced 27004 in
-- production data — it was purely a registry stub with no leaves,
-- no Chroma collection, no tenant_standards enrolments.
-- The DELETE will fail loudly (FK violation) if we ever missed one.

COMMIT;
