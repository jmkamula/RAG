-- schema_v110_client_facts_journey.sql
--
-- Ship 106'.a (2026-09-03) — capture tenant's compliance journey status
-- at onboarding. Set via Profile page, persisted alongside existing
-- client_facts fields since journey is a tenant-attribute (not
-- runtime state).
--
-- Five discrete states covering the maturity spectrum from greenfield
-- through mature-cite-mode. Not enforced/mutable — tenant can revisit
-- as they progress. Used by Get Started rendering (Ship 107' if we
-- want journey-driven personalization) + auditor-context surfaces.
--
-- Storing on client_facts rather than a new tenant_onboarding table
-- because client_facts is already the "who is this tenant" source of
-- truth and RLS/policies/grants are already correct there.

BEGIN;

ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS journey_status TEXT
        CHECK (journey_status IS NULL OR journey_status IN (
            'greenfield',   -- just starting, building from scratch
            'building',     -- some policies drafted, program not mature
            'documented',   -- full documentation set, not yet audited
            'audited',      -- been through internal/external audit ≥1x
            'mature'        -- program cites operational systems for evidence
        ));

ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS journey_status_updated_at TIMESTAMPTZ;

COMMIT;
