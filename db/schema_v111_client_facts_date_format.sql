-- schema_v111_client_facts_date_format.sql
--
-- Ship 108'.b (2026-09-03) — regional date-format preference on
-- client_facts. Different markets format dates differently (EMEA
-- DD/MM/YYYY, US MM/DD/YYYY, Central-EU DD.MM.YYYY, etc.). The
-- renderer applies the tenant's chosen format when substituting
-- date placeholders (<<GENERATED_DATE>>, whisper hints for
-- <<APPROVAL_DATE>> + <<NEXT_REVIEW_DATE>>).
--
-- Five canonical formats:
--   iso        — 2026-09-03      (ISO 8601, default, unambiguous)
--   dmy_slash  — 03/09/2026      (UK, Ireland, most of Europe, Brazil)
--   mdy_slash  — 09/03/2026      (US, Canada English)
--   dmy_dot    — 03.09.2026      (Germany, Czech Republic, Poland)
--   long       — 3 Sep 2026      (long form, unambiguous, wordy)
--
-- Default is NULL (renderer treats NULL as 'iso'). Tenant sets via
-- Profile → Regional preferences dropdown; auto-saves on change.

BEGIN;

ALTER TABLE public.client_facts
    ADD COLUMN IF NOT EXISTS date_format TEXT
        CHECK (date_format IS NULL OR date_format IN (
            'iso', 'dmy_slash', 'mdy_slash', 'dmy_dot', 'long'
        ));

COMMIT;
