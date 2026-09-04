-- schema_v114_sector_backfill_and_check.sql
--
-- Ship 114'.b (2026-09-04) — normalize legacy free-text sector values
-- to canonical codes (from rag/scoping/sectors.py) + add a CHECK
-- constraint locking the client_facts.sector column to the 21-value
-- vocabulary.
--
-- Design:
--   1. Backfill known free-text variants → canonical codes.
--   2. Any residual free-text values not covered by the map → NULL
--      (safe default; tenant re-picks via the Profile dropdown).
--   3. Add CHECK constraint. From this migration onward, any INSERT
--      or UPDATE with a non-canonical sector value fails at the DB
--      boundary.
--
-- Idempotent:
--   · The UPDATEs are self-check (`WHERE sector = ...`) so re-running
--     just no-ops after the first application.
--   · ADD CONSTRAINT IF NOT EXISTS ensures the CHECK doesn't error
--     on re-application.
--
-- Coverage:
--   Legacy variants observed so far:
--     · "technology" (dev Arion Networks tenant)
--     · "IT Consulting" (arionlabs-dr-01 Arion Networks s.r.o. tenant)
--
--   Additional expected variants defensively mapped (matches common
--   phrasings people type in free-text sector fields). Add more here
--   as new values surface in production.

BEGIN;

-- ── Backfill: legacy free-text → canonical code ─────────────────
UPDATE public.client_facts SET sector = 'ict_services'
 WHERE sector IN (
     'technology', 'Technology', 'tech', 'Tech',
     'IT', 'it', 'IT Consulting', 'it consulting',
     'IT services', 'IT Services',
     'cybersecurity', 'Cybersecurity',
     'security', 'Security',
     'software', 'Software', 'software company', 'saas', 'SaaS',
     'cloud', 'Cloud'
 );

UPDATE public.client_facts SET sector = 'banking'
 WHERE sector IN (
     'finance', 'Finance',
     'financial services', 'Financial services', 'Financial Services',
     'bank', 'Bank', 'Banking'
 );

UPDATE public.client_facts SET sector = 'finance_markets'
 WHERE sector IN (
     'trading', 'Trading',
     'exchange', 'Exchange',
     'capital markets', 'Capital Markets'
 );

UPDATE public.client_facts SET sector = 'health'
 WHERE sector IN (
     'healthcare', 'Healthcare',
     'medical', 'Medical',
     'pharma', 'Pharma', 'pharmaceutical', 'Pharmaceutical', 'pharmaceuticals'
 );

UPDATE public.client_facts SET sector = 'retail'
 WHERE sector IN (
     'retail', 'Retail',
     'ecommerce', 'E-commerce', 'e-commerce',
     'consumer', 'Consumer', 'consumer goods'
 );

UPDATE public.client_facts SET sector = 'professional'
 WHERE sector IN (
     'consulting', 'Consulting',
     'legal', 'Legal', 'law', 'Law',
     'accounting', 'Accounting',
     'professional services', 'Professional Services'
 );

UPDATE public.client_facts SET sector = 'manufacturing'
 WHERE sector IN (
     'manufacturing', 'Manufacturing',
     'industrial', 'Industrial'
 );

UPDATE public.client_facts SET sector = 'energy'
 WHERE sector IN (
     'energy', 'Energy',
     'utilities', 'Utilities',
     'oil', 'gas', 'electricity'
 );

UPDATE public.client_facts SET sector = 'transport'
 WHERE sector IN (
     'transport', 'Transport',
     'logistics', 'Logistics',
     'shipping', 'Shipping',
     'aviation', 'Aviation'
 );

UPDATE public.client_facts SET sector = 'public_admin'
 WHERE sector IN (
     'government', 'Government',
     'public sector', 'Public sector', 'Public Sector',
     'public administration'
 );

UPDATE public.client_facts SET sector = 'nonprofit'
 WHERE sector IN (
     'nonprofit', 'Nonprofit', 'non-profit', 'Non-profit',
     'ngo', 'NGO',
     'charity', 'Charity',
     'foundation', 'Foundation'
 );

UPDATE public.client_facts SET sector = 'research'
 WHERE sector IN (
     'research', 'Research',
     'academic', 'Academic',
     'university', 'University'
 );

UPDATE public.client_facts SET sector = 'digital_providers'
 WHERE sector IN (
     'media', 'Media',
     'social media', 'Social Media',
     'platform', 'Platform'
 );

-- ── Residual sweep: anything not in the canonical vocabulary → NULL ──
-- Safer than dropping the row or the migration. Tenant re-picks from
-- the Profile dropdown next time they visit the section.
UPDATE public.client_facts SET sector = NULL
 WHERE sector IS NOT NULL
   AND sector NOT IN (
     'energy', 'transport', 'banking', 'finance_markets',
     'health', 'water', 'digital_infra', 'ict_services',
     'public_admin', 'space',
     'postal_courier', 'waste_management', 'chemicals',
     'food', 'manufacturing', 'digital_providers', 'research',
     'retail', 'professional', 'nonprofit', 'other'
   );

-- ── Add CHECK constraint ─────────────────────────────────────────
-- Postgres doesn't have a native ADD CONSTRAINT IF NOT EXISTS for
-- CHECK, so guard with a DO block that checks pg_constraint.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conname = 'client_facts_sector_check'
           AND conrelid = 'public.client_facts'::regclass
    ) THEN
        ALTER TABLE public.client_facts
            ADD CONSTRAINT client_facts_sector_check
            CHECK (sector IS NULL OR sector IN (
                'energy', 'transport', 'banking', 'finance_markets',
                'health', 'water', 'digital_infra', 'ict_services',
                'public_admin', 'space',
                'postal_courier', 'waste_management', 'chemicals',
                'food', 'manufacturing', 'digital_providers', 'research',
                'retail', 'professional', 'nonprofit', 'other'
            ));
    END IF;
END $$;

COMMIT;
