-- schema_v113_client_facts_regions_and_size_bucket.sql
--
-- Ship 113'.a (2026-09-04) — extend client_facts region coverage from
-- 2 buckets (EU/EEA + UK) to 6 buckets covering the world, and add a
-- coarse employee-count bucket for the "under 50 / 50-250 / 250+"
-- Profile question that the boolean employee_count_250_plus alone
-- can't capture.
--
-- New region columns:
--   us_data_subjects          — United States
--   ca_data_subjects          — Canada
--   apac_data_subjects        — Asia-Pacific (includes Australia, NZ,
--                                Japan, Singapore, India, etc.)
--   other_data_subjects       — Latin America, Africa, Middle East,
--                                and anywhere else not covered above
--
-- Existing region columns (unchanged): eu_data_subjects, uk_data_subjects.
--
-- New employee-count column:
--   employee_size_bucket TEXT CHECK IN ('small','medium','large')
--     small   = 1-50 employees
--     medium  = 51-250 employees
--     large   = 251+ employees
--
-- employee_count_250_plus (existing boolean) stays — it's the specific
-- fact several applicability rules check. Ship 113'.b's Profile write
-- path populates BOTH the bucket + the boolean atomically.
--
-- Idempotent: uses IF NOT EXISTS. Additive columns only — no data
-- migration needed, existing rows get FALSE defaults.

BEGIN;

ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS us_data_subjects    BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS ca_data_subjects    BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS apac_data_subjects  BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS other_data_subjects BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS employee_size_bucket TEXT
        CHECK (employee_size_bucket IS NULL OR employee_size_bucket IN (
            'small', 'medium', 'large'
        ));

COMMIT;
