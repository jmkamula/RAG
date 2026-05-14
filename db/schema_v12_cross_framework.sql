-- ArionComply Schema v12 — Cross-framework attribution for risks, audits, incident_documents
-- Safe to run on top of v11.
--
-- Motivation: cross-framework audit (see commits e33f822 + follow-up) found three
-- artifacts with single-framework assumptions baked into the data model:
--   risks.isms_controls / pims_controls    — framework hardcoded as column names
--   isms_audits.standard_id (scalar)       — can't represent combined audits
--   incident_documents (no standard_id)    — collapses cross-framework evidence
--
-- Migration is idempotent — re-running is safe.

BEGIN;

-- ── risks: unified control_refs storing STANDARD:VERSION:REF entries ─────────
--
-- Existing data in isms_controls / pims_controls is the workbook text form
-- ("5.15 Access control"). Parse the leading ref token, prefix with the
-- appropriate framework, drop the legacy columns.

ALTER TABLE risks
    ADD COLUMN IF NOT EXISTS control_refs TEXT[] DEFAULT '{}';

UPDATE risks
   SET control_refs = (
        SELECT array_agg(s_ref ORDER BY s_ref)
        FROM (
            SELECT DISTINCT 'ISO27001:2022:' || split_part(c, ' ', 1) AS s_ref
              FROM unnest(COALESCE(isms_controls, '{}'::text[])) AS c
              WHERE c IS NOT NULL AND c <> ''
            UNION
            SELECT DISTINCT 'ISO27701:2019:' || split_part(c, ' ', 1) AS s_ref
              FROM unnest(COALESCE(pims_controls, '{}'::text[])) AS c
              WHERE c IS NOT NULL AND c <> ''
        ) sub
   )
 WHERE (isms_controls IS NOT NULL AND array_length(isms_controls, 1) > 0)
    OR (pims_controls IS NOT NULL AND array_length(pims_controls, 1) > 0);

ALTER TABLE risks DROP COLUMN IF EXISTS isms_controls;
ALTER TABLE risks DROP COLUMN IF EXISTS pims_controls;

-- ── isms_audits: standard_id (scalar) → standard_ids (array) ────────────────
--
-- A single surveillance audit may cover ISO 27001 AND ISO 27701 together.
-- Scalar default 'ISO27001:2022' forced that to be lost. Move to array.

ALTER TABLE isms_audits
    ADD COLUMN IF NOT EXISTS standard_ids TEXT[] NOT NULL DEFAULT '{}';

UPDATE isms_audits
   SET standard_ids = ARRAY[standard_id]
 WHERE standard_id IS NOT NULL
   AND (standard_ids IS NULL OR array_length(standard_ids, 1) IS NULL);

ALTER TABLE isms_audits ALTER COLUMN standard_ids DROP DEFAULT;
ALTER TABLE isms_audits DROP COLUMN IF EXISTS standard_id;

-- ── incident_documents: add standard_id to primary key ──────────────────────
--
-- A piece of incident evidence may simultaneously satisfy ISO A.5.24 and
-- GDPR Art.33. Old PK (incident_id, document_id) collapsed those rows.
-- Table currently has 0 rows so no data migration required.

ALTER TABLE incident_documents
    ADD COLUMN IF NOT EXISTS standard_id TEXT NOT NULL DEFAULT 'ISO27001:2022';

-- Drop default — must be supplied by writer going forward
ALTER TABLE incident_documents ALTER COLUMN standard_id DROP DEFAULT;

-- Replace PK to include standard_id
ALTER TABLE incident_documents DROP CONSTRAINT IF EXISTS incident_documents_pkey;
ALTER TABLE incident_documents
    ADD CONSTRAINT incident_documents_pkey
    PRIMARY KEY (incident_id, document_id, standard_id);

COMMIT;
