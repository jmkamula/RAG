-- schema_v112_client_facts_scoping_consolidation.sql
--
-- Ship 110'.a (2026-09-03) — clarify the client_facts table as the
-- single source of truth for compliance scoping attributes.
--
-- Historical drift: `tenants` accumulated overlapping scoping columns
-- (sector / industry / country / employee_count / cloud_only /
-- has_physical_premises / does_software_development) that duplicate
-- semantics already covered by client_facts booleans. Read paths were
-- inconsistent — some checked tenants, some checked client_facts —
-- and Quickstart wrote only to tenants, leaving client_facts at all
-- defaults (FALSE) so applies_when clauses saw a fictional tenant.
--
-- This migration:
--   1. Adds the missing scoping columns to client_facts (country,
--      employee_count) so all compliance-scoping attributes live in
--      one place.
--   2. Adds `fact_source` JSONB — per-column provenance tracking so
--      the applicability derivation can distinguish "tenant declared
--      this" from "we initialised it at Quickstart".
--   3. Adds `applicability_reason` TEXT on posture_controls — human-
--      readable narrative for why the engine set applicability_status
--      to 'na' (e.g. "cloud-only tenant — physical controls").
--   4. Backfills client_facts from tenants for existing tenants.
--   5. Leaves the tenants columns in place for now (deprecate + drop
--      in a follow-up migration once all read sites are migrated).
--
-- Idempotent: uses IF NOT EXISTS + safe backfill semantics.

BEGIN;

-- 1. Scoping columns migrated from tenants
ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS country        TEXT,
    ADD COLUMN IF NOT EXISTS employee_count INTEGER;

-- 2. Per-column fact-source provenance
--
-- Shape: {
--   "processes_personal_data": {"source": "declared",  "at": "2026-09-03T..."},
--   "eu_data_subjects":        {"source": "derived",   "at": "2026-09-03T..."},
--   "special_category_data":   {"source": "default",   "at": "2026-09-03T..."},
--   ...
-- }
--
-- Sources:
--   default    — initialised at Quickstart, never explicitly declared
--   declared   — tenant answered explicitly (Profile questionnaire)
--   derived    — computed from another fact or from evidence
--   overridden — tenant explicitly overrode a derived value
ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS fact_source JSONB NOT NULL DEFAULT '{}'::jsonb;

-- 3. Human-readable narrative for applicability derivation
ALTER TABLE public.posture_controls
    ADD COLUMN IF NOT EXISTS applicability_reason TEXT;

-- 4. Backfill scoping columns for existing tenants that already have
-- a client_facts row (do not create rows for tenants without one —
-- Ship 110'.b's Quickstart initializer covers that path).
UPDATE public.client_facts cf
   SET country        = COALESCE(cf.country, t.country),
       employee_count = COALESCE(cf.employee_count, t.employee_count)
  FROM public.tenants t
 WHERE cf.tenant_id = t.id
   AND (cf.country IS NULL OR cf.employee_count IS NULL);

-- Backfill the has_physical_premises boolean where a tenants row has
-- cloud_only=TRUE and client_facts still has the column-default TRUE.
-- (has_physical_premises has DEFAULT true so this catches Quickstart-
-- initialised tenants where the truth is cloud-only.)
UPDATE public.client_facts cf
   SET has_physical_premises = FALSE
  FROM public.tenants t
 WHERE cf.tenant_id = t.id
   AND t.cloud_only = TRUE
   AND cf.has_physical_premises = TRUE
   AND (cf.fact_source ->> 'has_physical_premises') IS NULL;

-- 5. Mark all existing non-default column values as 'declared' with
-- a backfill timestamp. Per user's instruction: "the stage at which
-- a client is shouldnt matter" — treat existing tenant state as
-- authoritative rather than tentative-derived.
--
-- We flag as declared:
--   · sector (has non-null value)
--   · country (has value after backfill)
--   · employee_count (has value after backfill)
--   · every boolean column that is not at its schema default
--
-- Columns at schema default remain marked 'default' (absent from the
-- fact_source jsonb — 110'.d treats absence as default).
UPDATE public.client_facts cf
   SET fact_source = fact_source ||
       jsonb_strip_nulls(jsonb_build_object(
         'sector',                    CASE WHEN cf.sector IS NOT NULL          THEN jsonb_build_object('source','declared','at', now()) END,
         'country',                   CASE WHEN cf.country IS NOT NULL         THEN jsonb_build_object('source','declared','at', now()) END,
         'employee_count',            CASE WHEN cf.employee_count IS NOT NULL  THEN jsonb_build_object('source','declared','at', now()) END,
         'processes_personal_data',   CASE WHEN cf.processes_personal_data     THEN jsonb_build_object('source','declared','at', now()) END,
         'eu_data_subjects',          CASE WHEN cf.eu_data_subjects            THEN jsonb_build_object('source','declared','at', now()) END,
         'uk_data_subjects',          CASE WHEN cf.uk_data_subjects            THEN jsonb_build_object('source','declared','at', now()) END,
         'role_controller',           CASE WHEN cf.role_controller             THEN jsonb_build_object('source','declared','at', now()) END,
         'role_processor',            CASE WHEN cf.role_processor              THEN jsonb_build_object('source','declared','at', now()) END,
         'role_joint_controller',     CASE WHEN cf.role_joint_controller       THEN jsonb_build_object('source','declared','at', now()) END,
         'special_category_data',     CASE WHEN cf.special_category_data       THEN jsonb_build_object('source','declared','at', now()) END,
         'criminal_conviction_data',  CASE WHEN cf.criminal_conviction_data    THEN jsonb_build_object('source','declared','at', now()) END,
         'childrens_data',            CASE WHEN cf.childrens_data              THEN jsonb_build_object('source','declared','at', now()) END,
         'automated_decision_making', CASE WHEN cf.automated_decision_making   THEN jsonb_build_object('source','declared','at', now()) END,
         'profiling',                 CASE WHEN cf.profiling                   THEN jsonb_build_object('source','declared','at', now()) END,
         'large_scale_processing',    CASE WHEN cf.large_scale_processing      THEN jsonb_build_object('source','declared','at', now()) END,
         'systematic_monitoring',     CASE WHEN cf.systematic_monitoring       THEN jsonb_build_object('source','declared','at', now()) END,
         'high_risk_processing',      CASE WHEN cf.high_risk_processing        THEN jsonb_build_object('source','declared','at', now()) END,
         'employee_count_250_plus',   CASE WHEN cf.employee_count_250_plus     THEN jsonb_build_object('source','declared','at', now()) END,
         'public_authority',          CASE WHEN cf.public_authority            THEN jsonb_build_object('source','declared','at', now()) END,
         'uses_processors',           CASE WHEN cf.uses_processors             THEN jsonb_build_object('source','declared','at', now()) END,
         'uses_cloud_services',       CASE WHEN cf.uses_cloud_services         THEN jsonb_build_object('source','declared','at', now()) END,
         'transfers_data_outside_eu', CASE WHEN cf.transfers_data_outside_eu   THEN jsonb_build_object('source','declared','at', now()) END,
         'develops_software',         CASE WHEN cf.develops_software           THEN jsonb_build_object('source','declared','at', now()) END,
         'has_remote_workers',        CASE WHEN cf.has_remote_workers          THEN jsonb_build_object('source','declared','at', now()) END,
         'has_physical_premises',     CASE WHEN NOT cf.has_physical_premises   THEN jsonb_build_object('source','declared','at', now()) END
       ))
 WHERE cf.fact_source = '{}'::jsonb;

COMMIT;
