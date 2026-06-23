-- Data fix 2026-06-23: normalize bare Annex A refs from workbook re-upload.
--
-- Background: the 2026-06-23 workbook re-upload (ebf724de) wrote 262
-- findings, of which 168 used bare numbering (5.x/6.x/7.x/8.x) for
-- Annex A controls instead of the canonical A-prefix form (A.5.x etc.).
-- The workbook source data uses a tenant-friendly convention where
-- ISMS clauses AND Annex A both appear as bare numbers; the
-- normalize_control_ref function (post-[[normalizer-annex-a-isms-collision]])
-- correctly refuses to auto-prefix because the 2-dot bands overlap.
--
-- Disambiguation rule for THIS data fix (per evidence inspection):
--   - 5.[4-37]  → A.5.x  (ISMS clause 5 only goes 5.1-5.3)
--   - 6.[4-8]   → A.6.x  (ISMS clause 6 only goes 6.1-6.3 plus 6.1.x)
--   - 7.[6-14]  → A.7.x  (ISMS clause 7 only goes 7.1-7.5)
--   - 8.[4-34]  → A.8.x  (ISMS clause 8 only goes 8.1-8.3)
--   - Ambiguous bands (5.1-3, 6.1-3, 7.1-5, 8.1-3) LEFT BARE —
--     evidence confirms these are ISMS clauses in this workbook
--     (Competence Records → 7.2, ISMS Objectives → 6.2, Change Mgmt Log → 6.3, etc.)
--   - 4.x, 9.x, 10.x always ISMS only
--
-- Also retires the 79 duplicate posture_controls rows the workbook
-- created at bare refs that have A-prefixed counterparts already
-- active.
--
-- This is per-tenant data, not a migration. Idempotent — safe to re-run.

\set ON_ERROR_STOP on

BEGIN;

-- 1. Normalize document_findings on the 2026-06-23 workbook upload
UPDATE document_findings df
SET control_ref =
  CASE
    WHEN df.control_ref ~ '^5\.([4-9]|[1-3][0-9])$'
         AND substring(df.control_ref FROM 3)::int BETWEEN 4 AND 37   THEN 'A.' || df.control_ref
    WHEN df.control_ref ~ '^6\.[4-8]$'                                 THEN 'A.' || df.control_ref
    WHEN df.control_ref ~ '^7\.([6-9]|1[0-4])$'                        THEN 'A.' || df.control_ref
    WHEN df.control_ref ~ '^8\.([4-9]|[1-3][0-9])$'
         AND substring(df.control_ref FROM 3)::int BETWEEN 4 AND 34   THEN 'A.' || df.control_ref
    ELSE df.control_ref
  END
FROM client_documents cd
WHERE df.document_id = cd.id
  AND cd.filename ILIKE '%workbook%Arion%'
  AND df.is_active = TRUE
  AND df.extracted_at >= '2026-06-23 13:55:00'
  AND df.extracted_at < '2026-06-23 14:00:00';

-- 2. Retire the bare-prefix posture_controls rows the workbook
--    created when an A-prefixed equivalent already exists
UPDATE posture_controls pc_bare
SET is_active = FALSE,
    last_updated = now()
FROM posture_controls pc_a
WHERE pc_bare.tenant_id = '00000000-0000-0000-0000-000000000001'
  AND pc_a.tenant_id   = '00000000-0000-0000-0000-000000000001'
  AND pc_a.is_active = TRUE
  AND pc_bare.is_active = TRUE
  AND pc_a.control_ref = 'A.' || pc_bare.control_ref
  AND pc_bare.control_ref ~ '^[5-8]\.'
  AND pc_bare.last_updated >= '2026-06-23 13:55:00';

COMMIT;
