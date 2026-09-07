-- schema_v118_diagnostic_log_delete_restriction.sql
--
-- Ship 127'.a (2026-09-07) — gate DELETE on the 7 diagnostic-log
-- tables behind a SECURITY DEFINER function owned by arioncomply
-- (the owner role). The app role can EXECUTE the function; it can
-- no longer DELETE from the tables directly.
--
-- Why: Ship 4'.b (schema_v79, 2026-07-17) granted DELETE to
-- arioncomply_app on 5 diagnostic tables so a future retention
-- sweep could run under the app role. That sweep was never built —
-- Ship 124'.c agent security review flagged the standing DELETE as
-- a same-tenant self-erasure risk (a tenant admin, or an attacker
-- with the admin key, could silently prune their own diagnostic
-- entries via raw SQL). RLS scopes the blast radius to same-tenant,
-- but the "no silent erasure" invariant we hold for compliance-
-- load-bearing tables (Ship 121') should also apply here.
--
-- The fix trades "app role has raw DELETE" for "app role can call a
-- named function that DELETEs — the function is auditable, its
-- signature encodes retention semantics, and swapping it for a
-- provenance-logging variant later is one function-body change".
--
-- Tables covered (7):
--   ai_call_log, chat_casefile_log, chat_consensus_log,
--   fact_recompute_log, intake_trace_log, intake_consensus_log,
--   request_trace_log
--
-- What DOESN'T change:
--   · SELECT + INSERT grants — unchanged (app writes rows normally)
--   · UPDATE — remains REVOKED (Ship 4'.b addendum discipline)
--   · Owner role — still has full DDL access as always
--   · RLS policies — unchanged; the function inherits owner-role
--     access which bypasses RLS, so callers must pass a tenant
--     filter as an argument (see WHERE clause in function body).

BEGIN;

-- ── 1. The function ──────────────────────────────────────────────
--
-- Table name is validated against an inline allowlist (7 tables); a
-- caller cannot inject arbitrary SQL through the table_name argument.
-- Retention window is expressed in days; both tenant_id (optional —
-- when NULL sweeps across all tenants) and retention_days are
-- required.
--
-- Returns the row count deleted for logging.

CREATE OR REPLACE FUNCTION public.sweep_delete_diagnostic_log_rows(
    p_table_name    text,
    p_retention_days integer,
    p_tenant_id     uuid DEFAULT NULL
) RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    allowed_tables constant text[] := ARRAY[
        'ai_call_log',
        'chat_casefile_log',
        'chat_consensus_log',
        'fact_recompute_log',
        'intake_trace_log',
        'intake_consensus_log',
        'request_trace_log'
    ];
    ts_column      text;
    where_tenant   text := '';
    sql_text       text;
    deleted_count  integer;
BEGIN
    -- Validate table_name against allowlist (prevents SQL injection
    -- via table_name arg + prevents accidental cross-class deletes)
    IF NOT (p_table_name = ANY(allowed_tables)) THEN
        RAISE EXCEPTION 'sweep_delete_diagnostic_log_rows: table_name % is not in allowlist (%)',
            p_table_name, allowed_tables;
    END IF;

    -- Validate retention_days (must be positive integer)
    IF p_retention_days IS NULL OR p_retention_days < 1 THEN
        RAISE EXCEPTION 'sweep_delete_diagnostic_log_rows: p_retention_days must be >= 1, got %',
            p_retention_days;
    END IF;

    -- Column name for the created-at timestamp varies across tables.
    -- Most use `created_at`; a couple use different names historically.
    -- Look up the actual column at call time so schema drift on one
    -- table doesn't silently no-op the sweep.
    SELECT column_name INTO ts_column
      FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = p_table_name
       AND column_name IN ('created_at', 'called_at', 'started_at', 'timestamp', 'ts')
     ORDER BY CASE column_name
                WHEN 'created_at' THEN 1
                WHEN 'called_at'  THEN 2
                WHEN 'started_at' THEN 3
                WHEN 'timestamp'  THEN 4
                WHEN 'ts'         THEN 5
              END
     LIMIT 1;

    IF ts_column IS NULL THEN
        RAISE EXCEPTION 'sweep_delete_diagnostic_log_rows: no timestamp column found on %',
            p_table_name;
    END IF;

    -- Optional tenant filter
    IF p_tenant_id IS NOT NULL THEN
        where_tenant := format(' AND tenant_id = %L::uuid', p_tenant_id);
    END IF;

    -- Build + execute the DELETE. quote_ident on table + column names.
    -- retention_days interpolated as %s (integer, safe).
    sql_text := format(
        'DELETE FROM public.%I WHERE %I < NOW() - INTERVAL ''%s days''%s',
        p_table_name,
        ts_column,
        p_retention_days,
        where_tenant
    );

    EXECUTE sql_text;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Owned by arioncomply so SECURITY DEFINER runs as owner (bypasses
-- app-role RLS + honors owner-role DELETE privilege on the tables).
ALTER FUNCTION public.sweep_delete_diagnostic_log_rows(text, integer, uuid)
    OWNER TO arioncomply;

-- ── 2. Revoke DELETE on the 7 diagnostic tables from arioncomply_app ──
--
-- App role can no longer issue raw DELETE. It can call the function
-- above (see grant below).
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT unnest(ARRAY[
        'ai_call_log',
        'chat_casefile_log',
        'chat_consensus_log',
        'fact_recompute_log',
        'intake_trace_log',
        'intake_consensus_log',
        'request_trace_log'
    ]) LOOP
        IF to_regclass('public.' || quote_ident(t)) IS NOT NULL THEN
            EXECUTE format('REVOKE DELETE ON public.%I FROM arioncomply_app', t);
        END IF;
    END LOOP;
END $$;

-- ── 3. Grant EXECUTE on the function to the app role ─────────────
REVOKE ALL ON FUNCTION public.sweep_delete_diagnostic_log_rows(text, integer, uuid)
    FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.sweep_delete_diagnostic_log_rows(text, integer, uuid)
    TO arioncomply_app;

-- ── 4. Document the intent ───────────────────────────────────────
COMMENT ON FUNCTION public.sweep_delete_diagnostic_log_rows(text, integer, uuid) IS
'Ship 127''.a — SECURITY DEFINER retention sweep entry point for the 7 diagnostic-log tables. Table_name is validated against a hardcoded allowlist; retention_days must be positive; optional tenant_id filter. Returns row count deleted. App role has EXECUTE only; raw DELETE on the underlying tables is REVOKED. Future retention sweep should call this function via the arioncomply_app connection.';

COMMIT;
