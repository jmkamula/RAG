-- ArionComply — post-baseline OWNER + GRANT reconciliation.
--
-- schema_baseline.sql is a pg_dump snapshot generated with
-- --no-owner --no-privileges, so when applied via
-- `sudo -u postgres psql -f schema_baseline.sql`:
--   1. every table / view / sequence / function ends up owned by
--      `postgres` (not by `arioncomply`, the intended schema owner)
--   2. neither app role has any privileges — reads and writes fail
--      with `permission denied for table X`
--
-- This file reassigns ownership to `arioncomply` and grants the
-- runtime privileges to `arioncomply_app`. Also sets DEFAULT
-- PRIVILEGES so future `schema_vN.sql` migrations that create new
-- objects (owned by `arioncomply` per its default role) automatically
-- grant the app role — no need to remember explicit GRANT clauses
-- in every new migration.
--
-- Idempotent: safe to re-run. ALTER TABLE ... OWNER TO is a no-op
-- when the target is already the owner; GRANTs are set-based and
-- ignore already-present entries.

-- ── Reassign ownership on every existing public object ──
DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER TABLE public.%I OWNER TO arioncomply', r.tablename);
    END LOOP;
    FOR r IN SELECT viewname FROM pg_views WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER VIEW public.%I OWNER TO arioncomply', r.viewname);
    END LOOP;
    FOR r IN SELECT matviewname FROM pg_matviews WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER MATERIALIZED VIEW public.%I OWNER TO arioncomply', r.matviewname);
    END LOOP;
    FOR r IN SELECT sequencename FROM pg_sequences WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER SEQUENCE public.%I OWNER TO arioncomply', r.sequencename);
    END LOOP;
    FOR r IN
        SELECT p.proname,
               pg_get_function_identity_arguments(p.oid) AS args
          FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'public'
    LOOP
        EXECUTE format(
            'ALTER FUNCTION public.%I(%s) OWNER TO arioncomply',
            r.proname, r.args
        );
    END LOOP;
END $$;

-- ── Grants for the app role ──
GRANT USAGE ON SCHEMA public TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA public TO arioncomply_app;
GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA public TO arioncomply_app;
GRANT EXECUTE
    ON ALL FUNCTIONS IN SCHEMA public TO arioncomply_app;

-- ── Default privileges for future migrations ──
-- Objects that `arioncomply` creates in future migrations
-- automatically grant the app role. Removes the need to write
-- `GRANT ... TO arioncomply_app` at the bottom of every new
-- schema_vN.sql — though existing migrations still do so
-- redundantly which is harmless.
ALTER DEFAULT PRIVILEGES FOR ROLE arioncomply IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO arioncomply_app;
ALTER DEFAULT PRIVILEGES FOR ROLE arioncomply IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO arioncomply_app;
ALTER DEFAULT PRIVILEGES FOR ROLE arioncomply IN SCHEMA public
    GRANT EXECUTE ON FUNCTIONS TO arioncomply_app;
