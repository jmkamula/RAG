-- ArionComply Postgres bootstrap — run once as `postgres` superuser
-- before applying schema_baseline.sql + seed_curator_data.sql.
--
-- Creates the two roles the API needs + the two databases + the
-- required extensions in each. Idempotent: safe to re-run on an
-- already-provisioned cluster.
--
-- Passwords are read from psql variables so the caller doesn't have
-- to touch this file:
--   psql -U postgres \
--        -v arion_owner_pass="$OWNER_PW" \
--        -v arion_app_pass="$APP_PW" \
--        -f deploy/postgres_preamble.sql

-- ── Roles ───────────────────────────────────────────────────────────
-- arioncomply       — schema owner; used by migrations + admin scripts
-- arioncomply_app   — RLS-scoped application user; the FastAPI pool
--                     uses this. RLS policies enforce per-tenant
--                     isolation via set_config('app.tenant_id', ...).
--
-- Psql variable interpolation (:'var') doesn't work inside DO blocks;
-- use SELECT ... \gexec to build the CREATE ROLE + ALTER ROLE statements
-- as query results and execute them. Also runs ALTER ROLE unconditionally
-- so re-running the preamble updates the password.

SELECT format('CREATE ROLE arioncomply LOGIN PASSWORD %L', :'arion_owner_pass')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'arioncomply')
\gexec

SELECT format('ALTER ROLE arioncomply PASSWORD %L', :'arion_owner_pass')
\gexec

SELECT format('CREATE ROLE arioncomply_app LOGIN PASSWORD %L', :'arion_app_pass')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'arioncomply_app')
\gexec

SELECT format('ALTER ROLE arioncomply_app PASSWORD %L', :'arion_app_pass')
\gexec

-- ── Databases ───────────────────────────────────────────────────────
-- Split: compliance data + LangGraph session checkpointer.
SELECT 'CREATE DATABASE arioncomply_compliance OWNER arioncomply'
 WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'arioncomply_compliance')
\gexec

SELECT 'CREATE DATABASE arioncomply_sessions OWNER arioncomply'
 WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'arioncomply_sessions')
\gexec

-- ── Extensions per DB ───────────────────────────────────────────────
\c arioncomply_compliance
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

\c arioncomply_sessions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
