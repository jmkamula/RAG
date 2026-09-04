-- ArionComply — Postgres schema baseline (arioncomply_compliance)
-- Generated: 2026-09-04T15:19:06Z from HEAD d20e85b8 by scripts/build_pg_baseline.sh
-- Includes: all public-schema DDL (tables / views / functions /
--          indexes / constraints / policies). Excludes: OWNER +
--          GRANT (applied post-hoc by baseline_grants.sql) and
--          the schema_migrations tracker (created by install.sh).
--          Zero tenant data — this is DDL-only.
-- Apply order: schema_baseline.sql → baseline_grants.sql → seed_curator_data.sql

--
-- PostgreSQL database dump
--

\restrict 1Fyc0JUNnLuDV7qXy6ZYfiLyEJQdz8F2odL6ngkqRoQbVbfiO5ZI2WG1PrKNhAb

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: fn_block_confirmation_log_delete(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_block_confirmation_log_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE EXCEPTION
        'confirmation_log is append-only — deletions are not permitted. '
        'Control ref: %, performed_at: %',
        OLD.control_ref, OLD.performed_at
    USING ERRCODE = '23000';  -- integrity_constraint_violation
END;
$$;


--
-- Name: fn_block_request_trace_delete(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_block_request_trace_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE EXCEPTION
        'request_trace_log is append-only — deletions not permitted. '
        'request_id: %, traced_at: %',
        OLD.request_id, OLD.traced_at
    USING ERRCODE = '23000';
END;
$$;


--
-- Name: fn_bulk_confirm_posture(uuid, uuid, text, text, boolean); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_bulk_confirm_posture(p_tenant_id uuid, p_confirmed_by uuid, p_standard_id text DEFAULT NULL::text, p_source text DEFAULT NULL::text, p_dry_run boolean DEFAULT true) RETURNS TABLE(control_ref text, finding text, source text, action text)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_batch_id  UUID := gen_random_uuid();
    v_rec       RECORD;
    v_count     INT  := 0;
BEGIN
    FOR v_rec IN
        SELECT pc.id, pc.control_ref AS v_ref, pc.finding AS v_finding,
               pc.source AS v_src, pc.standard_id AS v_std
        FROM posture_controls pc
        WHERE pc.tenant_id           = p_tenant_id
          AND pc.confirmation_status = 'draft'
          AND pc.is_active           = TRUE
          AND (p_standard_id IS NULL OR pc.standard_id = p_standard_id)
          AND (p_source      IS NULL OR pc.source      = p_source)
        ORDER BY pc.standard_id, pc.control_ref
    LOOP
        control_ref := v_rec.v_ref;
        finding     := v_rec.v_finding;
        source      := v_rec.v_src;

        IF p_dry_run THEN
            action := 'would_confirm';
        ELSE
            UPDATE posture_controls SET
                confirmation_status = 'confirmed',
                confirmed_by        = p_confirmed_by,
                confirmed_at        = NOW()
            WHERE id = v_rec.id;

            INSERT INTO confirmation_log (
                tenant_id, posture_control_id, control_ref, standard_id,
                action, previous_status, new_status,
                previous_finding, new_finding,
                performed_by, source, batch_id
            ) VALUES (
                p_tenant_id, v_rec.id, v_rec.v_ref, v_rec.v_std,
                'bulk_confirmed', 'draft', 'confirmed',
                v_rec.v_finding, v_rec.v_finding,
                p_confirmed_by, v_rec.v_src, v_batch_id
            );

            v_count := v_count + 1;
            action  := 'confirmed';
        END IF;

        RETURN NEXT;
    END LOOP;

    IF NOT p_dry_run THEN
        RAISE NOTICE 'Bulk confirmation complete: % findings confirmed (batch_id: %)',
            v_count, v_batch_id;
    END IF;
END;
$$;


--
-- Name: fn_compute_purge_after(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_compute_purge_after() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_retain_years INT;
    v_retain_days  INT;
    v_class        TEXT;
BEGIN
    -- Only fire when transitioning to inactive
    IF OLD.is_active = TRUE AND NEW.is_active = FALSE THEN
        v_class := NEW.retention_class;

        -- Look up retention period: table-specific first, then class default
        SELECT retain_years, retain_days
        INTO   v_retain_years, v_retain_days
        FROM   retention_policies
        WHERE  tenant_id IS NULL
          AND  retention_class = v_class
          AND  table_name = TG_TABLE_NAME
        LIMIT 1;

        IF NOT FOUND THEN
            SELECT retain_years, retain_days
            INTO   v_retain_years, v_retain_days
            FROM   retention_policies
            WHERE  tenant_id IS NULL
              AND  retention_class = v_class
              AND  table_name IS NULL
            LIMIT 1;
        END IF;

        -- Compute purge_after
        IF v_retain_years > 0 THEN
            NEW.purge_after := NOW() + (v_retain_years || ' years')::INTERVAL;
        ELSIF v_retain_days > 0 THEN
            NEW.purge_after := NOW() + (v_retain_days || ' days')::INTERVAL;
        ELSE
            -- personal_data class: erasure request — no fixed purge window
            NEW.purge_after := NULL;
        END IF;

        NEW.deleted_at := NOW();
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: fn_confirm_posture(uuid, uuid, uuid, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_confirm_posture(p_posture_id uuid, p_tenant_id uuid, p_confirmed_by uuid, p_action text DEFAULT 'confirmed'::text) RETURNS TABLE(v_control_ref text, v_finding text, v_status text)
    LANGUAGE sql SECURITY DEFINER
    AS $$
    UPDATE posture_controls
    SET confirmation_status = p_action,
        confirmed_by        = p_confirmed_by,
        confirmed_at        = NOW()
    WHERE id                  = p_posture_id
      AND tenant_id           = p_tenant_id
      AND is_active           = TRUE
      AND confirmation_status = 'draft'
    RETURNING control_ref, finding, confirmation_status;
$$;


--
-- Name: fn_handle_erasure_request(uuid, text, uuid, boolean); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_handle_erasure_request(p_tenant_id uuid, p_data_subject_ref text, p_requested_by uuid, p_dry_run boolean DEFAULT true) RETURNS TABLE(table_name text, records_found bigint, action_taken text)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Users table — anonymise name and email
    table_name    := 'users';
    records_found := 0;
    action_taken  := CASE WHEN p_dry_run THEN 'would_anonymise' ELSE 'anonymised' END;

    SELECT count(*) INTO records_found
    FROM users
    WHERE tenant_id = p_tenant_id
      AND (email = p_data_subject_ref OR name = p_data_subject_ref)
      AND is_active = TRUE;

    IF NOT p_dry_run AND records_found > 0 THEN
        UPDATE users SET
            name          = '[anonymised]',
            email         = '[anonymised-' || id || ']',
            anonymised_at = NOW(),
            deletion_reason = 'erasure_request'
        WHERE tenant_id = p_tenant_id
          AND (email = p_data_subject_ref OR name = p_data_subject_ref);

        INSERT INTO deletion_log
            (tenant_id, table_name, record_id, deletion_type,
             reason, requested_by, executed_at, retention_class)
        SELECT p_tenant_id, 'users', id, 'erasure',
               'erasure_request', p_requested_by, NOW(), 'personal_data'
        FROM users
        WHERE tenant_id = p_tenant_id
          AND email = '[anonymised-' || id || ']';
    END IF;
    RETURN NEXT;

    -- Vendors table — anonymise contact information
    table_name    := 'vendors';
    SELECT count(*) INTO records_found
    FROM vendors
    WHERE tenant_id = p_tenant_id
      AND is_active = TRUE;
    -- Vendors are legal entities not data subjects — no anonymisation needed
    -- unless contact_name is a natural person
    action_taken := 'not_applicable';
    records_found := 0;
    RETURN NEXT;

END;
$$;


--
-- Name: fn_override_posture(uuid, uuid, uuid, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_override_posture(p_posture_id uuid, p_tenant_id uuid, p_confirmed_by uuid, p_finding text, p_gap_description text DEFAULT NULL::text) RETURNS TABLE(v_control_ref text, v_finding text, v_status text)
    LANGUAGE sql SECURITY DEFINER
    AS $$
    UPDATE posture_controls
    SET confirmation_status = 'overridden',
        confirmed_by        = p_confirmed_by,
        confirmed_at        = NOW(),
        finding             = p_finding,
        gap_description     = COALESCE(p_gap_description, gap_description)
    WHERE id        = p_posture_id
      AND tenant_id = p_tenant_id
      AND is_active = TRUE
    RETURNING control_ref, finding, confirmation_status;
$$;


--
-- Name: fn_posture_confirmation_guard(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_posture_confirmation_guard() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_user_id   UUID;
    v_action    TEXT;
BEGIN
    v_user_id := NULLIF(current_setting('app.user_id', TRUE), '')::UUID;

    IF OLD.confirmation_status = NEW.confirmation_status THEN
        RETURN NEW;
    END IF;

    -- draft → confirmed: requires a confirmed_by user (v7 contract preserved).
    IF OLD.confirmation_status = 'draft'
       AND NEW.confirmation_status = 'confirmed' THEN
        IF NEW.confirmed_by IS NULL AND v_user_id IS NULL THEN
            RAISE EXCEPTION
                'Cannot confirm posture control % without a confirmed_by user',
                NEW.id
            USING ERRCODE = '23514';
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'confirmed';

    -- confirmed → draft: allowed when new evidence invalidates a confirmation.
    ELSIF OLD.confirmation_status = 'confirmed'
          AND NEW.confirmation_status = 'draft' THEN
        NEW.confirmed_by := NULL;
        NEW.confirmed_at := NULL;
        v_action := 'reverted_to_draft';

    -- any → overridden: human override path (v7 contract preserved).
    ELSIF NEW.confirmation_status = 'overridden' THEN
        IF NEW.system_finding IS NULL THEN
            NEW.system_finding     := OLD.finding;
            NEW.system_gap         := OLD.gap_description;
            NEW.system_proposed_at := OLD.updated_at;
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'overridden';

    -- HITL Stage-1: any → document_confirmed
    -- Performer resolution: explicit NEW.confirmed_by → app.user_id setting →
    -- per-tenant chat-user fallback (seeded above). The fallback keeps
    -- confirmation_log.performed_by NOT NULL satisfied until session-bound
    -- user ids land.
    ELSIF NEW.confirmation_status = 'document_confirmed' THEN
        NEW.confirmed_by := COALESCE(
            NEW.confirmed_by,
            v_user_id,
            (SELECT id FROM users
              WHERE tenant_id = NEW.tenant_id
                AND email = 'chat-user-' || NEW.tenant_id::text
                            || '@arioncomply.internal'
              LIMIT 1)
        );
        NEW.confirmed_at := NOW();
        v_action := 'document_confirmed';

    -- HITL Stage-2: any → engine_confirmed
    -- Same performer fallback as Stage-1. The Stage-2 chat surface also
    -- writes engine_approved_by / engine_approved_at separately on the
    -- posture_controls row; the confirmation_log entry captures the same
    -- performer for cross-table joins.
    ELSIF NEW.confirmation_status = 'engine_confirmed' THEN
        NEW.confirmed_by := COALESCE(
            NEW.confirmed_by,
            v_user_id,
            (SELECT id FROM users
              WHERE tenant_id = NEW.tenant_id
                AND email = 'chat-user-' || NEW.tenant_id::text
                            || '@arioncomply.internal'
              LIMIT 1)
        );
        NEW.confirmed_at := NOW();
        v_action := 'engine_confirmed';

    ELSE
        RAISE EXCEPTION
            'Invalid confirmation state transition: % → % for control %',
            OLD.confirmation_status, NEW.confirmation_status, NEW.control_ref
        USING ERRCODE = '23514';
    END IF;

    INSERT INTO confirmation_log (
        tenant_id, posture_control_id, control_ref, standard_id,
        action, previous_status, new_status,
        previous_finding, new_finding,
        performed_by, source
    ) VALUES (
        NEW.tenant_id, NEW.id, NEW.control_ref, NEW.standard_id,
        v_action, OLD.confirmation_status, NEW.confirmation_status,
        OLD.finding, NEW.finding,
        COALESCE(NEW.confirmed_by, v_user_id),
        NEW.source
    );

    RETURN NEW;
END;
$$;


--
-- Name: fn_posture_controls_to_assertion(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_posture_controls_to_assertion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    actor          text;
    prior_id       bigint;
    new_id         bigint;
BEGIN
    -- Skip noise: only fire when an actor-attributable column changes.
    IF TG_OP = 'UPDATE' THEN
        IF NEW.finding         IS NOT DISTINCT FROM OLD.finding
           AND NEW.source         IS NOT DISTINCT FROM OLD.source
           AND NEW.gap_description IS NOT DISTINCT FROM OLD.gap_description
           AND NEW.confidence     IS NOT DISTINCT FROM OLD.confidence THEN
            RETURN NEW;
        END IF;
    END IF;

    actor := CASE NEW.source
        WHEN 'workbook'        THEN 'tenant'
        WHEN 'chat'            THEN 'tenant'
        WHEN 'questionnaire'   THEN 'tenant'
        WHEN 'document'        THEN 'tenant'
        WHEN 'self_reported'   THEN 'tenant'
        WHEN 'Not assessed'    THEN 'tenant'
        WHEN 'engine'          THEN 'engine'
        WHEN 'engine_backfill' THEN 'engine'
        WHEN 'assessor'        THEN 'assessor'
        ELSE 'tenant'
    END;

    -- Supersede prior active assertion for this (tenant, control, std, actor).
    UPDATE posture_assertions
       SET status        = 'superseded',
           superseded_at = now()
     WHERE tenant_id   = NEW.tenant_id
       AND control_ref = NEW.control_ref
       AND standard_id = NEW.standard_id
       AND source      = actor
       AND status      = 'active'
     RETURNING id INTO prior_id;

    INSERT INTO posture_assertions (
        tenant_id, control_ref, standard_id, source,
        finding, gap_description, confidence,
        set_by, status, metadata
    ) VALUES (
        NEW.tenant_id, NEW.control_ref, NEW.standard_id, actor,
        NEW.finding, NEW.gap_description, NEW.confidence,
        'trigger:' || NEW.source, 'active',
        jsonb_build_object(
            'posture_controls_id',    NEW.id,
            'pc_source',              NEW.source,
            'pc_confirmation_status', NEW.confirmation_status
        )
    )
    RETURNING id INTO new_id;

    IF prior_id IS NOT NULL THEN
        UPDATE posture_assertions
           SET superseded_by_id = new_id
         WHERE id = prior_id;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: fn_posture_write_guard(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_posture_write_guard() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_current_role TEXT := current_user;
    v_user_id      TEXT := NULLIF(current_setting('app.user_id', TRUE), '');
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF v_current_role = 'arioncomply_app'
           AND NEW.confirmation_status != 'draft' THEN
            RAISE EXCEPTION
                'arioncomply_app can only insert draft posture findings. Got: %',
                NEW.confirmation_status
            USING ERRCODE = '42501';
        END IF;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF v_current_role = 'arioncomply_app'
           AND v_user_id IS NULL
           AND OLD.confirmation_status = 'draft'
           AND NEW.confirmation_status IN ('confirmed', 'overridden') THEN
            RAISE EXCEPTION
                'arioncomply_app cannot confirm posture findings without app.user_id set.'
            USING ERRCODE = '42501';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: fn_purge_expired_records(boolean); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_purge_expired_records(p_dry_run boolean DEFAULT true) RETURNS TABLE(table_name text, records_purged bigint, records_skipped bigint)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    t           TEXT;
    v_count     BIGINT;
    v_skipped   BIGINT;
    v_class     TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        -- Only auto_purge = TRUE classes
        'assets', 'risks', 'vendors',
        'remediation_plans', 'remediation_tasks', 'remediation_evidence',
        'client_documents',
        'users', 'user_roles',
        'tenant_standards', 'notifications'
        -- NOT: posture_controls, isms_audits, incidents — compliance class, manual review
    ]
    LOOP
        IF p_dry_run THEN
            EXECUTE format(
                'SELECT count(*) FROM %I
                 WHERE is_active = FALSE
                   AND purge_after IS NOT NULL
                   AND purge_after < NOW()',
                t
            ) INTO v_count;
            v_skipped := 0;
        ELSE
            -- Log before purging
            EXECUTE format(
                'INSERT INTO deletion_log
                    (tenant_id, table_name, record_id, deletion_type,
                     reason, retention_class, executed_at)
                 SELECT tenant_id, %L, id, ''purge'',
                        ''retention_expired'', retention_class, NOW()
                 FROM %I
                 WHERE is_active = FALSE
                   AND purge_after IS NOT NULL
                   AND purge_after < NOW()',
                t, t
            );

            -- Physical delete
            EXECUTE format(
                'WITH deleted AS (
                    DELETE FROM %I
                    WHERE is_active = FALSE
                      AND purge_after IS NOT NULL
                      AND purge_after < NOW()
                    RETURNING 1
                 ) SELECT count(*) FROM deleted',
                t
            ) INTO v_count;

            v_skipped := 0;
        END IF;

        table_name     := t;
        records_purged := CASE WHEN p_dry_run THEN 0 ELSE v_count END;
        records_skipped:= CASE WHEN p_dry_run THEN v_count ELSE 0 END;
        RETURN NEXT;
    END LOOP;
END;
$$;


--
-- Name: fn_purge_failed_uploads(integer, boolean); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_purge_failed_uploads(p_older_than_days integer DEFAULT 30, p_dry_run boolean DEFAULT true) RETURNS TABLE(tenant_id uuid, rows_candidate bigint, rows_purged bigint, oldest_uploaded timestamp with time zone, newest_uploaded timestamp with time zone)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_cutoff TIMESTAMPTZ := NOW() - (p_older_than_days || ' days')::INTERVAL;
BEGIN
    IF p_dry_run THEN
        RETURN QUERY
            SELECT du.tenant_id,
                   COUNT(*)::BIGINT          AS rows_candidate,
                   0::BIGINT                 AS rows_purged,
                   MIN(du.uploaded_at)       AS oldest_uploaded,
                   MAX(du.uploaded_at)       AS newest_uploaded
              FROM document_uploads du
             WHERE du.extraction_status = 'failed'
               AND du.uploaded_at       < v_cutoff
             GROUP BY du.tenant_id;
        RETURN;
    END IF;

    RETURN QUERY
        WITH deleted AS (
            DELETE FROM document_uploads du
             WHERE du.extraction_status = 'failed'
               AND du.uploaded_at       < v_cutoff
            RETURNING tenant_id, uploaded_at
        )
        SELECT tenant_id,
               COUNT(*)::BIGINT,
               COUNT(*)::BIGINT,
               MIN(uploaded_at),
               MAX(uploaded_at)
          FROM deleted
         GROUP BY tenant_id;
END;
$$;


--
-- Name: fn_update_document_status(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_update_document_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- File just added (storage_path was NULL, now set)
    IF OLD.storage_path IS NULL AND NEW.storage_path IS NOT NULL THEN
        NEW.document_status  := 'uploaded';
        NEW.is_metadata_only := FALSE;
        NEW.status_reason    := 'File uploaded at ' ||
                                TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI');
    END IF;
    -- File removed (shouldn't happen but handle gracefully)
    IF OLD.storage_path IS NOT NULL AND NEW.storage_path IS NULL THEN
        NEW.document_status  := 'registered';
        NEW.is_metadata_only := TRUE;
        NEW.status_reason    := 'File removed at ' ||
                                TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI');
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;


--
-- Name: fn_workbook_intake_proposal_touch_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_workbook_intake_proposal_touch_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;


--
-- Name: next_platform_ref(uuid, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.next_platform_ref(p_tenant_id uuid, p_prefix text, p_tenant_short text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_seq INT;
    v_pad INT := CASE WHEN p_prefix IN ('INC', 'AUD') THEN 3 ELSE 4 END;
BEGIN
    INSERT INTO ref_sequences (tenant_id, prefix, next_seq)
    VALUES (p_tenant_id, p_prefix, 2)
    ON CONFLICT (tenant_id, prefix)
    DO UPDATE SET next_seq = ref_sequences.next_seq + 1
    RETURNING next_seq - 1 INTO v_seq;

    RETURN p_prefix || '-' || p_tenant_short || '-'
           || LPAD(v_seq::TEXT, v_pad, '0');
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_call_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_call_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    called_at timestamp with time zone DEFAULT now() NOT NULL,
    purpose text NOT NULL,
    provider text NOT NULL,
    model text NOT NULL,
    latency_ms integer,
    tokens_in integer,
    tokens_out integer,
    cost_usd numeric(12,6),
    prompt_hash text,
    prompt_preview text,
    response_hash text,
    response_preview text,
    error_type text,
    error_detail text,
    upload_id uuid,
    session_id text,
    request_id text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT ai_call_log_provider_check CHECK ((provider = ANY (ARRAY['openai'::text, 'anthropic'::text, 'other'::text]))),
    CONSTRAINT ai_call_log_purpose_check CHECK ((purpose = ANY (ARRAY['chat'::text, 'classifier'::text, 'polish'::text, 'polish_short_circuit'::text, 'rank_answer'::text, 'compose'::text, 'correct'::text, 'verify'::text, 'extractor'::text, 'extractor_pass2'::text, 'enricher'::text, 'xfw_proposer'::text, 'cascade'::text, 'embedding_query'::text, 'embedding_index'::text, 'consensus_gatekeeper'::text, 'enrichment_tier2'::text, 'guidance_gen'::text, 'other'::text])))
);


--
-- Name: TABLE ai_call_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.ai_call_log IS 'Diagnostic log for LLM call cost/latency/prompt debugging. NOT a compliance-evidence artifact — arioncomply_app has INSERT/SELECT/DELETE (retention-eligible), UPDATE explicitly revoked to prevent silent history rewrites.';


--
-- Name: COLUMN ai_call_log.purpose; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ai_call_log.purpose IS 'Tag identifying which pipeline stage made the LLM call. Kept in sync with rag/llm_client.py callers. Adding a new purpose? Bump this allowlist in the same migration that lands the new call site. See [[ship-5-prime-e-ai-call-log-purpose-allowlist-2026-07-18]].';


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_keys (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    user_id uuid NOT NULL,
    key_hash text NOT NULL,
    key_prefix text NOT NULL,
    name text NOT NULL,
    scopes text[] DEFAULT '{chat,hitl,documents,posture}'::text[] NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_used_at timestamp with time zone,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid
);


--
-- Name: api_rate_limit_bucket; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_rate_limit_bucket (
    key_id uuid NOT NULL,
    window_start timestamp with time zone DEFAULT date_trunc('minute'::text, now()) NOT NULL,
    count integer DEFAULT 0 NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT api_rate_limit_bucket_count_non_negative CHECK ((count >= 0))
);


--
-- Name: TABLE api_rate_limit_bucket; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.api_rate_limit_bucket IS 'Ship 4''.a: per-api_key fixed-window (1min) rate-limit counter for /api/external/v1/* endpoints.';


--
-- Name: COLUMN api_rate_limit_bucket.window_start; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.api_rate_limit_bucket.window_start IS 'Start of the current 1-minute window (date_trunc(''minute'',NOW())). Rolls over on next request past the window boundary.';


--
-- Name: applicable_standards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.applicable_standards (
    tenant_id uuid NOT NULL,
    standard_id text NOT NULL,
    in_scope boolean DEFAULT true NOT NULL,
    added_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'platform'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    external_ref text NOT NULL,
    name text NOT NULL,
    asset_type text,
    owner_text text,
    owner uuid,
    location text,
    value_classification text,
    cia_c text,
    cia_i text,
    cia_a text,
    comments text,
    personal_data_types text[],
    data_subject_categories text[],
    processing_purposes text[],
    retention_period text,
    contains_pii boolean DEFAULT false NOT NULL,
    workbook_imported boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT assets_cia_a_check CHECK (((cia_a = ANY (ARRAY['High'::text, 'Medium'::text, 'Low'::text])) OR (cia_a IS NULL))),
    CONSTRAINT assets_cia_c_check CHECK (((cia_c = ANY (ARRAY['High'::text, 'Medium'::text, 'Low'::text])) OR (cia_c IS NULL))),
    CONSTRAINT assets_cia_i_check CHECK (((cia_i = ANY (ARRAY['High'::text, 'Medium'::text, 'Low'::text])) OR (cia_i IS NULL))),
    CONSTRAINT assets_value_classification_check CHECK (((value_classification = ANY (ARRAY['High'::text, 'Medium'::text, 'Low'::text])) OR (value_classification IS NULL)))
);


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    user_id uuid,
    user_role text,
    action text NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    ip_address inet,
    user_agent text,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
)
PARTITION BY RANGE (created_at);


--
-- Name: audit_log_2025; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log_2025 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    user_id uuid,
    user_role text,
    action text NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    ip_address inet,
    user_agent text,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_2026; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log_2026 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    user_id uuid,
    user_role text,
    action text NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    ip_address inet,
    user_agent text,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_2027; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log_2027 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    user_id uuid,
    user_role text,
    action text NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    ip_address inet,
    user_agent text,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_2028; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log_2028 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    user_id uuid,
    user_role text,
    action text NOT NULL,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    ip_address inet,
    user_agent text,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cascade_suppression_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cascade_suppression_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    source_verification_id uuid NOT NULL,
    source_event_type text NOT NULL,
    target_event_type text,
    applies_when text NOT NULL,
    evaluation_context jsonb DEFAULT '{}'::jsonb NOT NULL,
    cascade_path jsonb DEFAULT '[]'::jsonb NOT NULL,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    suppression_kind text DEFAULT 'emits_event'::text NOT NULL,
    target_requirement_id text,
    CONSTRAINT cascade_suppression_log_applies_when_nonempty CHECK ((length(TRIM(BOTH FROM applies_when)) > 0)),
    CONSTRAINT cascade_suppression_log_consistency_chk CHECK ((((suppression_kind = 'emits_event'::text) AND (target_event_type IS NOT NULL)) OR ((suppression_kind = 'blocks_when'::text) AND (target_requirement_id IS NOT NULL)) OR ((suppression_kind = 'policy_override'::text) AND ((target_event_type IS NOT NULL) OR (target_requirement_id IS NOT NULL))))),
    CONSTRAINT cascade_suppression_log_kind_chk CHECK ((suppression_kind = ANY (ARRAY['emits_event'::text, 'blocks_when'::text, 'policy_override'::text])))
);


--
-- Name: TABLE cascade_suppression_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.cascade_suppression_log IS 'Append-only log of EMITS_EVENT edges whose applies_when evaluated false. Captures the path that was considered and consciously skipped, for auditor explanation of why a downstream cascade did not fire.';


--
-- Name: COLUMN cascade_suppression_log.suppression_kind; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.cascade_suppression_log.suppression_kind IS 'Which suppression mode fired this row: emits_event (S3d EMITS_EVENT applies_when=false) or blocks_when (S3i implication suppressed because a BLOCKS_WHEN blocker matched the cascade metadata).';


--
-- Name: COLUMN cascade_suppression_log.target_requirement_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.cascade_suppression_log.target_requirement_id IS 'For blocks_when: the control whose implication was suppressed. For emits_event: NULL.';


--
-- Name: chat_casefile_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_casefile_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    request_id text,
    session_id text,
    query text NOT NULL,
    question_type text,
    case_file_summary jsonb NOT NULL,
    system_prompt_tokens integer,
    user_digest_tokens integer,
    total_prompt_tokens integer,
    repair_events jsonb DEFAULT '[]'::jsonb NOT NULL,
    repair_events_count integer DEFAULT 0 NOT NULL,
    footers_added text[] DEFAULT '{}'::text[] NOT NULL,
    casefile_enabled boolean DEFAULT false NOT NULL,
    shadow_mode boolean DEFAULT false NOT NULL,
    digest_latency_ms integer,
    repair_latency_ms integer,
    total_latency_ms integer,
    error_type text,
    error_detail text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    purge_after timestamp with time zone,
    answer_text text,
    claim_events jsonb DEFAULT '[]'::jsonb NOT NULL,
    claim_events_count integer DEFAULT 0 NOT NULL
);


--
-- Name: TABLE chat_casefile_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.chat_casefile_log IS 'Diagnostic log for Ship 2'' case-file digest observability. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';


--
-- Name: COLUMN chat_casefile_log.case_file_summary; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.case_file_summary IS 'CaseFile.summary() diagnostic view: {query_len, question_type, cited_refs, primary_nodes, xfw_nodes, xfw_bridges, doc_contexts, posture_counts, active_session_refs}. Compact JSON for slicing without joining resolver traces.';


--
-- Name: COLUMN chat_casefile_log.repair_events; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.repair_events IS '[{kind: "missing_ref"|"missing_draft_near_ref"|"missing_verdict_near_ref"|"missing_bridge_footer", ref: "A.5.18", detail: "..."}]. High "missing_ref" rate = LLM dropping content; investigate whether the digest surfaced it.';


--
-- Name: COLUMN chat_casefile_log.casefile_enabled; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.casefile_enabled IS 'TRUE when Ship 2'' was active on this turn (CASEFILE_ENABLED=1). During rollout: compare token/repair distributions between enabled/disabled slices.';


--
-- Name: COLUMN chat_casefile_log.shadow_mode; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.shadow_mode IS 'TRUE when both paths ran but only one was served — shadow comparison. When True, casefile_enabled indicates which path was measured, not which was served.';


--
-- Name: COLUMN chat_casefile_log.answer_text; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.answer_text IS 'Ship 6''.d: full post-repair LLM answer, capped at 8000 chars. Feeds the passive claim scanner and any future observability arc. NULL for pre-6''.d rows.';


--
-- Name: COLUMN chat_casefile_log.claim_events; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_casefile_log.claim_events IS 'Ship 6''.d: passive claim-scan events. Array of {ref, verb, snippet, ref_in_digest, standard_in_scope}. See [[ship-6-prime-d-claim-scan-observability-2026-07-19]].';


--
-- Name: chat_consensus_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_consensus_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    request_id text,
    session_id text,
    query text NOT NULL,
    verdict text NOT NULL,
    top_refs text[],
    top_ref_confidence numeric(6,3),
    corroborators integer,
    question_type text,
    framework text,
    signals_json jsonb NOT NULL,
    disagreement_notes text[],
    clarification jsonb,
    llm_fallback_used boolean DEFAULT false NOT NULL,
    latency_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT ccl_verdict_check CHECK ((verdict = ANY (ARRAY['confident'::text, 'ambiguous'::text, 'insufficient'::text])))
);


--
-- Name: TABLE chat_consensus_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.chat_consensus_log IS 'Diagnostic log for Ship 1 consensus tuning. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';


--
-- Name: COLUMN chat_consensus_log.signals_json; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_consensus_log.signals_json IS 'JSON array of {name, refs:[[ref,weight],...], question_type, framework, metadata, fired}. Full audit trail of what each of the 7 consensus signals contributed for this turn.';


--
-- Name: COLUMN chat_consensus_log.llm_fallback_used; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.chat_consensus_log.llm_fallback_used IS 'TRUE when the legacy LLM classifier fired because consensus was insufficient. High rates indicate floors need tuning or coverage gaps in the deterministic signals.';


--
-- Name: chat_llm_decision_trail; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.chat_llm_decision_trail AS
 SELECT cf.id AS casefile_log_id,
    cf.tenant_id,
    cf.request_id,
    cf.session_id,
    cf.created_at AS turn_at,
    cf.query,
    cf.question_type,
    cs.verdict AS consensus_verdict,
    cs.top_refs AS consensus_top_refs,
    cs.top_ref_confidence AS consensus_top_conf,
    cs.corroborators AS consensus_corroborators,
    cs.framework AS consensus_framework,
    cs.llm_fallback_used AS consensus_llm_fallback,
    cf.system_prompt_tokens AS prompt_tokens_system,
    cf.user_digest_tokens AS prompt_tokens_digest,
    cf.total_prompt_tokens AS prompt_tokens_total,
    cf.repair_events_count,
    cf.footers_added,
    cf.digest_latency_ms,
    cf.repair_latency_ms,
    cf.total_latency_ms,
    cf.claim_events_count,
    cf.claim_events,
    length(cf.answer_text) AS answer_len,
    llm.n_calls AS llm_n_calls,
    llm.tokens_in_total AS llm_tokens_in,
    llm.tokens_out_total AS llm_tokens_out,
    llm.cost_total AS llm_cost_usd,
    llm.purposes AS llm_purposes,
    llm.models AS llm_models
   FROM ((public.chat_casefile_log cf
     LEFT JOIN public.chat_consensus_log cs ON (((cs.request_id = cf.request_id) AND (cs.tenant_id = cf.tenant_id))))
     LEFT JOIN LATERAL ( SELECT (count(*))::integer AS n_calls,
            (COALESCE(sum(al.tokens_in), (0)::bigint))::integer AS tokens_in_total,
            (COALESCE(sum(al.tokens_out), (0)::bigint))::integer AS tokens_out_total,
            (COALESCE(sum(al.cost_usd), (0)::numeric))::numeric(12,6) AS cost_total,
            array_agg(DISTINCT al.purpose ORDER BY al.purpose) AS purposes,
            array_agg(DISTINCT al.model ORDER BY al.model) AS models
           FROM public.ai_call_log al
          WHERE ((al.request_id = cf.request_id) AND (al.tenant_id = cf.tenant_id))) llm ON (true))
  WHERE (cf.request_id IS NOT NULL);


--
-- Name: VIEW chat_llm_decision_trail; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.chat_llm_decision_trail IS 'Ship 6''.e (2026-07-19): one row per chat turn joining chat_casefile_log ⋈ chat_consensus_log ⋈ ai_call_log on request_id. Auditor + engineer surface for tracing a full LLM decision trail. See [[ship-6-prime-e-decision-trail-view-2026-07-19]].';


--
-- Name: cite_attestation_prompt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cite_attestation_prompt (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    cite_id uuid NOT NULL,
    candidate_document_id uuid NOT NULL,
    must_id text NOT NULL,
    leaf_id text NOT NULL,
    control_ref text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by uuid,
    dismissed_reason text,
    verification_log_id uuid,
    expires_at timestamp with time zone DEFAULT (now() + '30 days'::interval) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    confidence text DEFAULT 'must_overlap'::text NOT NULL,
    CONSTRAINT cite_attestation_prompt_confidence_chk CHECK ((confidence = ANY (ARRAY['must_overlap'::text, 'url_and_must'::text]))),
    CONSTRAINT cite_attestation_prompt_leaf_id_format CHECK ((leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$'::text)),
    CONSTRAINT cite_attestation_prompt_must_id_format CHECK ((must_id ~ '^item:[A-Za-z0-9.]+:[a-z0-9_]+$'::text)),
    CONSTRAINT cite_attestation_prompt_resolution_consistent CHECK ((((status = 'pending'::text) AND (resolved_at IS NULL)) OR ((status = 'confirmed'::text) AND (resolved_at IS NOT NULL) AND (verification_log_id IS NOT NULL)) OR ((status = 'dismissed'::text) AND (resolved_at IS NOT NULL) AND (dismissed_reason IS NOT NULL)) OR ((status = 'auto_expired'::text) AND (resolved_at IS NOT NULL)))),
    CONSTRAINT cite_attestation_prompt_status_chk CHECK ((status = ANY (ARRAY['pending'::text, 'confirmed'::text, 'dismissed'::text, 'auto_expired'::text])))
);


--
-- Name: TABLE cite_attestation_prompt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.cite_attestation_prompt IS 'Ship 92''.b — tenant one-click cite attestation. Created on doc upload when a document has present findings on a MUST that has an active cite. Tenant confirms via dashboard; confirmation writes external_evidence_verification_log. Scale-invariant across URL shapes (SharePoint / Drive / OneDrive / Notion) because the signal is MUST overlap, not URL parsing.';


--
-- Name: COLUMN cite_attestation_prompt.confidence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.cite_attestation_prompt.confidence IS 'Ship 92''.f — signal quality behind the prompt. ''must_overlap'' (default, Ship 92''.b): uploaded doc has present findings on the same MUST as the cite. ''url_and_must'' (Ship 92''.f): the doc''s filename ALSO matches the cite URL basename ILIKE (Ship 92''.a-style URL match) IN ADDITION to MUST overlap. UI can visually escalate url_and_must to "strong match — one-click confirm recommended".';


--
-- Name: client_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    filename text NOT NULL,
    storage_path text,
    file_size_bytes integer,
    mime_type text,
    checksum_sha256 text,
    evidence_type text,
    document_title text,
    version text,
    full_text text,
    page_count integer,
    approved_by text,
    approval_date date,
    review_date date,
    document_owner text,
    topics_detected text[],
    standards_cited text[],
    control_refs text[],
    superseded_by uuid,
    is_current boolean DEFAULT true NOT NULL,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    uploaded_by uuid,
    chat_session_id text,
    expires_at timestamp with time zone,
    archived_at timestamp with time zone,
    external_ref text,
    approval_status text,
    is_metadata_only boolean DEFAULT false NOT NULL,
    workbook_imported boolean DEFAULT false NOT NULL,
    platform_ref text,
    document_status text DEFAULT 'registered'::text NOT NULL,
    status_reason text,
    last_reviewed_at timestamp with time zone,
    review_due_at timestamp with time zone,
    owner_name text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT client_documents_approval_status_check CHECK (((approval_status = ANY (ARRAY['Approved'::text, 'Pending'::text, 'Draft'::text, 'Superseded'::text])) OR (approval_status IS NULL))),
    CONSTRAINT client_documents_document_status_check CHECK ((document_status = ANY (ARRAY['registered'::text, 'uploaded'::text, 'processing'::text, 'active'::text, 'superseded'::text, 'withdrawn'::text])))
);


--
-- Name: client_fact_change_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_fact_change_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    fact_id text NOT NULL,
    operation text NOT NULL,
    old_value boolean,
    new_value boolean,
    applied boolean DEFAULT true NOT NULL,
    source_verification_id uuid NOT NULL,
    source_event_type text NOT NULL,
    rationale text,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT client_fact_change_log_operation_chk CHECK ((operation = ANY (ARRAY['set'::text, 'clear'::text, 'recompute'::text])))
);


--
-- Name: TABLE client_fact_change_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.client_fact_change_log IS 'Append-only audit of ClientFact mutations from cascade UPDATES_FACT edges. Captures who/when/why and the resulting state.';


--
-- Name: client_facts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_facts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    processes_personal_data boolean DEFAULT false NOT NULL,
    eu_data_subjects boolean DEFAULT false NOT NULL,
    uk_data_subjects boolean DEFAULT false NOT NULL,
    role_controller boolean DEFAULT false NOT NULL,
    role_processor boolean DEFAULT false NOT NULL,
    role_joint_controller boolean DEFAULT false NOT NULL,
    special_category_data boolean DEFAULT false NOT NULL,
    criminal_conviction_data boolean DEFAULT false NOT NULL,
    childrens_data boolean DEFAULT false NOT NULL,
    automated_decision_making boolean DEFAULT false NOT NULL,
    profiling boolean DEFAULT false NOT NULL,
    large_scale_processing boolean DEFAULT false NOT NULL,
    systematic_monitoring boolean DEFAULT false NOT NULL,
    high_risk_processing boolean DEFAULT false NOT NULL,
    employee_count_250_plus boolean DEFAULT false NOT NULL,
    public_authority boolean DEFAULT false NOT NULL,
    sector text,
    uses_processors boolean DEFAULT false NOT NULL,
    uses_cloud_services boolean DEFAULT false NOT NULL,
    transfers_data_outside_eu boolean DEFAULT false NOT NULL,
    develops_software boolean DEFAULT false NOT NULL,
    has_remote_workers boolean DEFAULT false NOT NULL,
    has_physical_premises boolean DEFAULT true NOT NULL,
    collected_via text DEFAULT 'questionnaire'::text,
    last_updated timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'platform'::text NOT NULL,
    purge_after timestamp with time zone,
    journey_status text,
    journey_status_updated_at timestamp with time zone,
    date_format text,
    country text,
    employee_count integer,
    fact_source jsonb DEFAULT '{}'::jsonb NOT NULL,
    us_data_subjects boolean DEFAULT false NOT NULL,
    ca_data_subjects boolean DEFAULT false NOT NULL,
    apac_data_subjects boolean DEFAULT false NOT NULL,
    other_data_subjects boolean DEFAULT false NOT NULL,
    employee_size_bucket text,
    CONSTRAINT client_facts_date_format_check CHECK (((date_format IS NULL) OR (date_format = ANY (ARRAY['iso'::text, 'dmy_slash'::text, 'mdy_slash'::text, 'dmy_dot'::text, 'long'::text])))),
    CONSTRAINT client_facts_employee_size_bucket_check CHECK (((employee_size_bucket IS NULL) OR (employee_size_bucket = ANY (ARRAY['small'::text, 'medium'::text, 'large'::text])))),
    CONSTRAINT client_facts_journey_status_check CHECK (((journey_status IS NULL) OR (journey_status = ANY (ARRAY['greenfield'::text, 'building'::text, 'documented'::text, 'audited'::text, 'mature'::text])))),
    CONSTRAINT client_facts_sector_check CHECK (((sector IS NULL) OR (sector = ANY (ARRAY['energy'::text, 'transport'::text, 'banking'::text, 'finance_markets'::text, 'health'::text, 'water'::text, 'digital_infra'::text, 'ict_services'::text, 'public_admin'::text, 'space'::text, 'postal_courier'::text, 'waste_management'::text, 'chemicals'::text, 'food'::text, 'manufacturing'::text, 'digital_providers'::text, 'research'::text, 'retail'::text, 'professional'::text, 'nonprofit'::text, 'other'::text]))))
);


--
-- Name: confirmation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confirmation_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    posture_control_id uuid NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    action text NOT NULL,
    previous_status text NOT NULL,
    new_status text NOT NULL,
    previous_finding text,
    new_finding text,
    performed_by uuid NOT NULL,
    performed_at timestamp with time zone DEFAULT now() NOT NULL,
    reason text,
    ip_address inet,
    source text NOT NULL,
    batch_id uuid,
    CONSTRAINT confirmation_log_action_check CHECK ((action = ANY (ARRAY['confirmed'::text, 'reverted_to_draft'::text, 'overridden'::text, 'bulk_confirmed'::text, 'document_confirmed'::text, 'engine_confirmed'::text])))
);


--
-- Name: control_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.control_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    control_id uuid NOT NULL,
    document_id uuid NOT NULL,
    relationship text DEFAULT 'evidences'::text NOT NULL,
    source text DEFAULT 'workbook'::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT control_documents_relationship_check CHECK ((relationship = ANY (ARRAY['evidences'::text, 'defines'::text, 'requires'::text, 'templates'::text])))
);


--
-- Name: deletion_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.deletion_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    table_name text NOT NULL,
    record_id uuid NOT NULL,
    deletion_type text NOT NULL,
    reason text NOT NULL,
    requested_by uuid,
    executed_by uuid,
    executed_at timestamp with time zone DEFAULT now() NOT NULL,
    retention_class text NOT NULL,
    record_snapshot jsonb,
    purge_scheduled timestamp with time zone,
    purge_verified_at timestamp with time zone,
    notes text,
    CONSTRAINT deletion_log_deletion_type_check CHECK ((deletion_type = ANY (ARRAY['soft'::text, 'anonymise'::text, 'purge'::text, 'erasure'::text]))),
    CONSTRAINT deletion_log_reason_check CHECK ((reason = ANY (ARRAY['erasure_request'::text, 'retention_expired'::text, 'tenant_offboarding'::text, 'admin'::text, 'test_data'::text])))
);


--
-- Name: posture_controls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_controls (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    standard_id text NOT NULL,
    control_ref text,
    node_id text,
    finding text DEFAULT 'Not assessed'::text NOT NULL,
    confidence text DEFAULT 'medium'::text NOT NULL,
    gap_description text,
    action_required text,
    risk_level text,
    evidence_present text[],
    evidence_required text[],
    remediation_status text DEFAULT 'open'::text NOT NULL,
    owner uuid,
    target_date date,
    source text DEFAULT 'Not assessed'::text NOT NULL,
    chat_session_id text,
    assessed_at timestamp with time zone DEFAULT now() NOT NULL,
    last_updated timestamp with time zone DEFAULT now() NOT NULL,
    external_ref text,
    soa_notes text,
    soa_justification text,
    linked_policies text[],
    owner_text text,
    workbook_imported boolean DEFAULT false NOT NULL,
    workbook_import_date timestamp with time zone,
    platform_ref text,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    confirmation_status text DEFAULT 'draft'::text NOT NULL,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    system_finding text,
    system_gap text,
    system_proposed_at timestamp with time zone,
    engine_proposed_at timestamp with time zone,
    engine_proposal_status text DEFAULT 'none'::text NOT NULL,
    engine_approved_by uuid,
    engine_approved_at timestamp with time zone,
    applicability_status text DEFAULT 'applicable'::text NOT NULL,
    applicability_reason text,
    CONSTRAINT posture_controls_applicability_status_check CHECK ((applicability_status = ANY (ARRAY['applicable'::text, 'na'::text]))),
    CONSTRAINT posture_controls_confidence_check CHECK ((confidence = ANY (ARRAY['high'::text, 'medium'::text, 'low'::text]))),
    CONSTRAINT posture_controls_confirmation_status_check CHECK ((confirmation_status = ANY (ARRAY['draft'::text, 'confirmed'::text, 'overridden'::text, 'document_confirmed'::text, 'engine_confirmed'::text]))),
    CONSTRAINT posture_controls_engine_proposal_status_check CHECK ((engine_proposal_status = ANY (ARRAY['none'::text, 'proposed'::text, 'approved'::text, 'rejected'::text]))),
    CONSTRAINT posture_controls_finding_check CHECK ((finding = ANY (ARRAY['NC'::text, 'OFI'::text, 'Comply'::text, 'N/A'::text, 'Not assessed'::text]))),
    CONSTRAINT posture_controls_remediation_status_check CHECK ((remediation_status = ANY (ARRAY['open'::text, 'in_progress'::text, 'closed'::text, 'accepted_risk'::text]))),
    CONSTRAINT posture_controls_risk_level_check CHECK ((risk_level = ANY (ARRAY['critical'::text, 'high'::text, 'medium'::text, 'low'::text, NULL::text]))),
    CONSTRAINT posture_controls_source_check CHECK ((source = ANY (ARRAY['chat'::text, 'questionnaire'::text, 'document'::text, 'assessor'::text, 'self_reported'::text, 'workbook'::text, 'Not assessed'::text, 'engine'::text, 'engine_backfill'::text])))
);


--
-- Name: document_alerts; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.document_alerts AS
 WITH doc_priority AS (
         SELECT cd.id,
            cd.tenant_id,
            cd.platform_ref,
            cd.external_ref,
            cd.document_title,
            cd.evidence_type AS document_type,
            cd.document_status,
            cd.filename,
            cd.approval_status,
            cd.version,
            cd.owner_name,
            cd.last_reviewed_at,
            cd.review_due_at,
            min(
                CASE pc.finding
                    WHEN 'NC'::text THEN 1
                    WHEN 'OFI'::text THEN 2
                    WHEN 'Comply'::text THEN 3
                    ELSE 4
                END) AS worst_finding_score,
            string_agg(DISTINCT pc.finding, ', '::text) AS linked_findings,
            array_agg(DISTINCT ((pc.standard_id || ':'::text) || pc.control_ref) ORDER BY ((pc.standard_id || ':'::text) || pc.control_ref)) FILTER (WHERE (pc.control_ref IS NOT NULL)) AS linked_control_refs,
            string_agg(DISTINCT ((pc.standard_id || ':'::text) || pc.control_ref), ', '::text ORDER BY ((pc.standard_id || ':'::text) || pc.control_ref)) FILTER (WHERE (pc.control_ref IS NOT NULL)) AS linked_controls,
            count(DISTINCT pc.id) AS control_count
           FROM ((public.client_documents cd
             LEFT JOIN public.control_documents ctd ON (((ctd.document_id = cd.id) AND (ctd.tenant_id = cd.tenant_id))))
             LEFT JOIN public.posture_controls pc ON (((pc.id = ctd.control_id) AND (pc.tenant_id = cd.tenant_id))))
          GROUP BY cd.id, cd.tenant_id, cd.platform_ref, cd.external_ref, cd.document_title, cd.evidence_type, cd.document_status, cd.filename, cd.approval_status, cd.version, cd.owner_name, cd.last_reviewed_at, cd.review_due_at
        )
 SELECT platform_ref,
    external_ref,
    document_title,
    document_status,
        CASE
            WHEN ((document_status = 'registered'::text) AND (worst_finding_score = 1)) THEN 'CRITICAL'::text
            WHEN ((document_status = 'registered'::text) AND (worst_finding_score = 2)) THEN 'WARNING'::text
            WHEN (document_status = 'registered'::text) THEN 'INFO'::text
            WHEN ((review_due_at IS NOT NULL) AND (review_due_at < now())) THEN 'WARNING'::text
            ELSE NULL::text
        END AS alert_type,
        CASE
            WHEN ((document_status = 'registered'::text) AND (worst_finding_score = 1)) THEN ('File not uploaded — required evidence for NC finding on '::text || COALESCE(linked_controls, 'unknown control'::text))
            WHEN ((document_status = 'registered'::text) AND (worst_finding_score = 2)) THEN ('File not uploaded — referenced by OFI finding on '::text || COALESCE(linked_controls, 'unknown control'::text))
            WHEN (document_status = 'registered'::text) THEN 'File not uploaded — registered as metadata only'::text
            WHEN ((review_due_at IS NOT NULL) AND (review_due_at < now())) THEN ('Review overdue since '::text || to_char(review_due_at, 'YYYY-MM-DD'::text))
            ELSE 'No action required'::text
        END AS alert_message,
    linked_controls,
    linked_control_refs,
    linked_findings,
    control_count,
    worst_finding_score,
    filename,
    version,
    owner_name,
    approval_status,
    last_reviewed_at,
    review_due_at,
    tenant_id
   FROM doc_priority;


--
-- Name: document_findings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_findings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    checklist_item_id text,
    status text NOT NULL,
    confidence text DEFAULT 'medium'::text NOT NULL,
    excerpt text,
    section_number text,
    page_number integer,
    requirement_text text,
    gdpr_required boolean DEFAULT false,
    extracted_at timestamp with time zone DEFAULT now() NOT NULL,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    expires_at timestamp with time zone,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    inferred_from_control_ref text,
    inferred_from_standard_id text,
    inference_source text DEFAULT 'extracted'::text NOT NULL,
    review_status text DEFAULT 'pending'::text NOT NULL,
    rejection_reason text,
    reviewed_by uuid,
    reviewed_at timestamp with time zone,
    workbook_proposal_id bigint,
    corroborating_signals text[] DEFAULT '{}'::text[] NOT NULL,
    grounding_method text,
    evidence_group_id text,
    resolved_by_upload_id uuid,
    resolved_at timestamp with time zone,
    resolution_reason text,
    CONSTRAINT document_findings_confidence_check CHECK ((confidence = ANY (ARRAY['high'::text, 'medium'::text, 'low'::text]))),
    CONSTRAINT document_findings_grounding_method_check CHECK (((grounding_method IS NULL) OR (grounding_method = ANY (ARRAY['extractor_verbatim'::text, 'workbook'::text, 'workbook_llm_arbiter'::text, 'template'::text, 'fingerprint'::text, 'leaf_scan'::text, 'manual'::text, 'form'::text, 'unknown'::text, 'structural'::text])))),
    CONSTRAINT document_findings_inference_source_check CHECK ((inference_source = ANY (ARRAY['extracted'::text, 'xfw_bridge'::text, 'regex_explicit'::text, 'llm_xfw'::text, 'workbook'::text, 'workbook_llm_arbiter'::text, 'leaf_scan'::text, 'form'::text, 'templated'::text, 'fingerprint_match'::text, 'structural_pattern'::text]))),
    CONSTRAINT document_findings_review_inactive_check CHECK (((review_status <> ALL (ARRAY['rejected'::text, 'expired'::text])) OR (is_active = false))),
    CONSTRAINT document_findings_review_status_check CHECK ((review_status = ANY (ARRAY['pending'::text, 'approved'::text, 'rejected'::text, 'expired'::text]))),
    CONSTRAINT document_findings_status_check CHECK ((status = ANY (ARRAY['present'::text, 'missing'::text, 'partial'::text])))
);


--
-- Name: COLUMN document_findings.inferred_from_control_ref; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.inferred_from_control_ref IS 'For xfw_bridge proposals: the source control_ref this finding mirrors. NULL for extracted findings.';


--
-- Name: COLUMN document_findings.inferred_from_standard_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.inferred_from_standard_id IS 'For xfw_bridge proposals: the source standard_id this finding mirrors. NULL for extracted findings.';


--
-- Name: COLUMN document_findings.inference_source; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.inference_source IS 'How the finding was inferred. Ship 91'' added workbook_llm_arbiter — LLM row-arbiter running after workbook_persistence structural pass, reads catalog three-way discipline (required/optional/cite) as scaffolding, emits per-row per-MUST findings the structural pass missed. Verified via substring-match to source cell.';


--
-- Name: COLUMN document_findings.corroborating_signals; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.corroborating_signals IS 'Wave 4a: which independent corroboration signals agreed the control was in scope at write-time. Read together with review_status to compute rolling per-signal precision. Values: target_controls / semantic_controls / explicit_refs / llm_extracted.';


--
-- Name: COLUMN document_findings.grounding_method; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.grounding_method IS 'Ship 6''.b — auditor-facing pathway label for how evidence was grounded. Ship 91''.b added workbook_llm_arbiter — LLM output substring-verified against source cell content at claimed (row, column) coordinates.';


--
-- Name: COLUMN document_findings.evidence_group_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.evidence_group_id IS 'Ship 42 dedup key: sha1(document_id || control_ref || normalized_excerpt)[:16]. Rows sharing the same evidence_group_id are UI-collapsed to a single auditor-facing citation but preserved individually for engine per-MUST recognition. NULL for legacy rows (pre-Ship-42); backfill script populates.';


--
-- Name: COLUMN document_findings.resolved_by_upload_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.resolved_by_upload_id IS 'Ship 93''.z.iii — nullable FK to the upload whose extraction produced a covering present finding on the same MUST. Set by the post-upload closure sweep in rag/posture/finding_closure.py. NULL means the finding hasn''t been resolved via upload (still active-partial, active-missing-tracked-elsewhere, or already closed for another reason like Stage-1 rejection).';


--
-- Name: COLUMN document_findings.resolved_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.resolved_at IS 'Ship 93''.z.iii — when the closure linkage was stamped. Distinct from extracted_at (source finding creation) and deleted_at (soft-delete). Populated together with resolved_by_upload_id.';


--
-- Name: COLUMN document_findings.resolution_reason; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.document_findings.resolution_reason IS 'Ship 93''.z.iii — auditor-facing narrative for the closure. Example: "upload of ‘Info Security Policy.docx’ produced present finding on same MUST item:A.5.9:owner_per_asset".';


--
-- Name: document_sections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_sections (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    section_number text,
    title text,
    text text NOT NULL,
    page_start integer,
    page_end integer,
    char_offset integer,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: document_text; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_text (
    upload_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    markdown text NOT NULL,
    markdown_sha256 text NOT NULL,
    source_sha256 text NOT NULL,
    converter text NOT NULL,
    byte_count integer NOT NULL,
    parsed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: document_upload_priority; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.document_upload_priority AS
 SELECT cd.platform_ref,
    cd.external_ref,
    cd.document_title,
    cd.filename,
    (cd.storage_path IS NOT NULL) AS has_file,
    cd.is_metadata_only,
    cd.document_status,
    cd.tenant_id,
    min(
        CASE pc.finding
            WHEN 'NC'::text THEN 1
            WHEN 'OFI'::text THEN 2
            WHEN 'Comply'::text THEN 3
            ELSE 4
        END) AS priority_score,
    string_agg(DISTINCT pc.control_ref, ', '::text ORDER BY pc.control_ref) AS linked_controls,
    string_agg(DISTINCT pc.finding, ', '::text) AS linked_findings
   FROM ((public.client_documents cd
     LEFT JOIN public.control_documents ctd ON (((ctd.document_id = cd.id) AND (ctd.tenant_id = cd.tenant_id))))
     LEFT JOIN public.posture_controls pc ON (((pc.id = ctd.control_id) AND (pc.tenant_id = cd.tenant_id))))
  GROUP BY cd.id, cd.platform_ref, cd.external_ref, cd.document_title, cd.filename, cd.storage_path, cd.is_metadata_only, cd.document_status, cd.tenant_id
  ORDER BY (min(
        CASE pc.finding
            WHEN 'NC'::text THEN 1
            WHEN 'OFI'::text THEN 2
            WHEN 'Comply'::text THEN 3
            ELSE 4
        END)), cd.external_ref;


--
-- Name: document_uploads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_uploads (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    filename text NOT NULL,
    storage_path text,
    doc_type text,
    standard_ids text[],
    extraction_path text,
    extraction_status text DEFAULT 'pending'::text NOT NULL,
    findings_count integer DEFAULT 0,
    token_estimate integer,
    error_message text,
    uploaded_by uuid,
    uploaded_at timestamp with time zone DEFAULT now(),
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    sha256 text,
    byte_size integer,
    dup_of_upload_id uuid,
    series_id uuid,
    version_no integer,
    CONSTRAINT document_uploads_extraction_path_check CHECK ((extraction_path = ANY (ARRAY['full_document'::text, 'section_based'::text, 'structured'::text, 'manual_review'::text]))),
    CONSTRAINT document_uploads_extraction_status_check CHECK ((extraction_status = ANY (ARRAY['pending'::text, 'processing'::text, 'completed'::text, 'failed'::text, 'manual_review'::text, 'duplicate'::text]))),
    CONSTRAINT document_uploads_series_version_paired CHECK ((((series_id IS NULL) AND (version_no IS NULL)) OR ((series_id IS NOT NULL) AND (version_no IS NOT NULL) AND (version_no >= 1))))
);


--
-- Name: enricher_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enricher_cache (
    sha256 text NOT NULL,
    doc_type text,
    standard_ids text[],
    topic_tokens text[],
    scope_statement text,
    cached_at timestamp with time zone DEFAULT now() NOT NULL,
    hit_count integer DEFAULT 0 NOT NULL,
    last_hit_at timestamp with time zone
);


--
-- Name: expected_followup_event; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expected_followup_event (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    source_verification_id uuid NOT NULL,
    source_event_type text NOT NULL,
    expected_event_type text NOT NULL,
    window_days integer NOT NULL,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    resolved_at timestamp with time zone,
    resolved_verification_id uuid,
    rationale text,
    CONSTRAINT expected_followup_event_resolution_consistent CHECK ((((status = 'pending'::text) AND (resolved_at IS NULL)) OR ((status = 'satisfied'::text) AND (resolved_at IS NOT NULL) AND (resolved_verification_id IS NOT NULL)) OR ((status = 'overdue'::text) AND (resolved_at IS NOT NULL) AND (resolved_verification_id IS NULL)))),
    CONSTRAINT expected_followup_event_status_chk CHECK ((status = ANY (ARRAY['pending'::text, 'satisfied'::text, 'overdue'::text]))),
    CONSTRAINT expected_followup_event_window_chk CHECK (((window_days >= 0) AND (window_days <= 3650)))
);


--
-- Name: TABLE expected_followup_event; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.expected_followup_event IS 'Per-tenant tracking of EXPECTS_FOLLOWUP_EVENT chains. Pending row -> awaiting matching downstream verification. Satisfied -> matched. Overdue -> window elapsed without match (sweep-derived).';


--
-- Name: external_evidence_source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.external_evidence_source (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    must_id text NOT NULL,
    leaf_id text NOT NULL,
    system_id uuid NOT NULL,
    cadence_days integer NOT NULL,
    per_must_note text,
    last_verified_at timestamp with time zone,
    next_review_due timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    origin_finding_id uuid,
    hyperlink_url text,
    hyperlink_display text,
    CONSTRAINT external_evidence_source_cadence_positive CHECK (((cadence_days >= 1) AND (cadence_days <= 3650))),
    CONSTRAINT external_evidence_source_leaf_id_format CHECK ((leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$'::text)),
    CONSTRAINT external_evidence_source_must_id_format CHECK ((must_id ~ '^item:[A-Za-z0-9.]+:[a-z0-9_]+$'::text))
);


--
-- Name: TABLE external_evidence_source; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.external_evidence_source IS 'Per-MUST cite rows. Each binds one checklist_item to one source system. UI groups by (system_id, leaf_id) for display.';


--
-- Name: COLUMN external_evidence_source.next_review_due; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_evidence_source.next_review_due IS 'last_verified_at + cadence_days. Application-maintained on each verification.';


--
-- Name: COLUMN external_evidence_source.origin_finding_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_evidence_source.origin_finding_id IS 'Ship 89''.b (2026-08-20) — nullable FK to the workbook document_finding that produced this cite via a `cite_columns:` YAML binding. When NULL, the cite was created outside the workbook path (tenant profile UI, manual admin action, etc.). Auditor lens: "which workbook row cited this?" answers via this attribution.';


--
-- Name: COLUMN external_evidence_source.hyperlink_url; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_evidence_source.hyperlink_url IS 'Ship 92''.a.i — the actual hyperlink URL captured from the matched workbook cite_columns cell. Used by Ship 92''.a.iii auto-verification resolver to compare against client_documents.filename on document upload. Nullable — pre-Ship-92 rows have no URL; new workbook_persistence emissions populate it. Multiple hyperlinks in the same cite column collapse to one cite via UNIQUE(tenant, must_id, system_id); this column stores the FIRST non-mailto URL discovered on the sheet.';


--
-- Name: COLUMN external_evidence_source.hyperlink_display; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_evidence_source.hyperlink_display IS 'Ship 92''.d — the cell display text captured alongside the hyperlink (openpyxl `Hyperlink.display` or the cell''s string value). Preferred for tenant-facing surfaces; the raw URL stays available in hyperlink_url for auditor drill-in. When multiple hyperlinks in the same cite column collapse to one cite row, this stores the FIRST non-empty display text.';


--
-- Name: external_evidence_verification_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.external_evidence_verification_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    system_id uuid NOT NULL,
    leaf_id text NOT NULL,
    verified_at timestamp with time zone DEFAULT now() NOT NULL,
    verified_by uuid NOT NULL,
    changes_detected text NOT NULL,
    sample_upload_id uuid,
    note text,
    musts_covered_count integer DEFAULT 0 NOT NULL,
    structured_events jsonb DEFAULT '[]'::jsonb NOT NULL,
    CONSTRAINT external_evidence_verification_log_changes_nonempty CHECK ((length(TRIM(BOTH FROM changes_detected)) > 0)),
    CONSTRAINT external_evidence_verification_log_leaf_id_format CHECK ((leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$'::text)),
    CONSTRAINT external_evidence_verification_log_structured_events_is_array CHECK ((jsonb_typeof(structured_events) = 'array'::text))
);


--
-- Name: TABLE external_evidence_verification_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.external_evidence_verification_log IS 'Append-only audit history of cite verifications. One row per (system, leaf, verify event). changes_detected REQUIRED — forces real review.';


--
-- Name: COLUMN external_evidence_verification_log.structured_events; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.external_evidence_verification_log.structured_events IS 'Optional array of structured event emissions for the cascade engine. Each element: {event_type, count, subject_refs?, metadata?}. event_type must match a known Event.event_type from enrichment/events/event_nodes.py.';


--
-- Name: fact_recompute_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fact_recompute_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    fact_key text NOT NULL,
    computed_value boolean,
    prior_value boolean,
    changed boolean NOT NULL,
    source_type text NOT NULL,
    error_type text,
    error_detail text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    latency_ms integer
);


--
-- Name: TABLE fact_recompute_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.fact_recompute_log IS 'Diagnostic log for Ship 3'' fact-recompute sweep observability. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';


--
-- Name: fact_source_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fact_source_config (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fact_key text NOT NULL,
    source_type text NOT NULL,
    source_query text,
    source_config jsonb DEFAULT '{}'::jsonb NOT NULL,
    refresh_days integer DEFAULT 7 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT fact_source_type_check CHECK ((source_type = ANY (ARRAY['sql'::text, 'posture'::text, 'evidence'::text, 'external'::text, 'llm'::text])))
);


--
-- Name: TABLE fact_source_config; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.fact_source_config IS 'UPDATES_FACT: source-of-truth definition per client_facts key. Recompute worker uses this to refresh facts periodically.';


--
-- Name: incident_classifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_classifications (
    incident_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    standard_id text NOT NULL,
    dimension text NOT NULL,
    value text NOT NULL,
    source text DEFAULT 'manual'::text NOT NULL,
    confidence numeric(4,3),
    classified_at timestamp with time zone DEFAULT now() NOT NULL,
    classified_by uuid,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT incident_classifications_source_check CHECK ((source = ANY (ARRAY['workbook'::text, 'manual'::text, 'api'::text, 'derived'::text, 'llm'::text])))
);


--
-- Name: incident_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_documents (
    incident_id uuid NOT NULL,
    document_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    document_role text NOT NULL,
    linked_at timestamp with time zone DEFAULT now() NOT NULL,
    linked_by uuid,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    standard_id text NOT NULL,
    CONSTRAINT incident_documents_document_role_check CHECK ((document_role = ANY (ARRAY['notification'::text, 'evidence'::text, 'response'::text, 'correspondence'::text, 'dpa'::text])))
);


--
-- Name: incident_obligations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_obligations (
    incident_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    deadline text,
    deadline_at timestamp with time zone,
    rationale text,
    is_met boolean DEFAULT false,
    met_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: incident_timeline; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_timeline (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    incident_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    event_type text NOT NULL,
    from_status text,
    to_status text,
    note text,
    actioned_by uuid,
    actioned_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incidents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    title text,
    description text,
    status text DEFAULT 'open'::text NOT NULL,
    severity text DEFAULT 'medium'::text NOT NULL,
    occurred_at timestamp with time zone,
    reported_at timestamp with time zone DEFAULT now() NOT NULL,
    deadline_at timestamp with time zone,
    notified_at timestamp with time zone,
    closed_at timestamp with time zone,
    affected_count_approx integer,
    affected_categories text[],
    affected_countries text[],
    created_by uuid,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    external_ref text,
    asset_ref text,
    pii_involved boolean,
    authority_notified boolean,
    data_subjects_notified boolean,
    lessons_learned text,
    pii_restoration_auth_by text,
    actions_taken text,
    evidence_collected boolean,
    workbook_imported boolean DEFAULT false NOT NULL,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT incidents_severity_check CHECK ((severity = ANY (ARRAY['critical'::text, 'high'::text, 'medium'::text, 'low'::text]))),
    CONSTRAINT incidents_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_progress'::text, 'closed'::text, 'withdrawn'::text])))
);


--
-- Name: intake_consensus_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.intake_consensus_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    upload_id uuid NOT NULL,
    logged_at timestamp with time zone DEFAULT now() NOT NULL,
    total_candidates integer NOT NULL,
    n_accept integer NOT NULL,
    n_arbiter integer NOT NULL,
    n_drop integer NOT NULL,
    n_arbiter_llm_accept integer DEFAULT 0 NOT NULL,
    n_arbiter_llm_reject integer DEFAULT 0 NOT NULL,
    signals_summary jsonb NOT NULL,
    candidates_sample jsonb,
    latency_ms integer,
    cost_usd numeric(10,6),
    retention_class text DEFAULT 'diagnostic'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: TABLE intake_consensus_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.intake_consensus_log IS 'Diagnostic log for Ship 33 extraction consensus module. One row per doc processed. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';


--
-- Name: intake_trace_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.intake_trace_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    trace_id text NOT NULL,
    tenant_id uuid NOT NULL,
    upload_id text,
    filename text NOT NULL,
    stage text NOT NULL,
    stage_status text DEFAULT 'ok'::text NOT NULL,
    stage_ms integer DEFAULT 0 NOT NULL,
    total_ms integer DEFAULT 0 NOT NULL,
    token_estimate integer,
    page_count integer,
    section_count integer,
    extraction_path text,
    doc_type text,
    standard_ids text[],
    explicit_refs_found integer,
    llm_calls integer,
    findings_raw integer,
    findings_kept integer,
    findings_written integer,
    posture_created integer,
    posture_updated integer,
    posture_skipped integer,
    error_type text,
    error_detail text,
    traced_at timestamp with time zone DEFAULT now() NOT NULL,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    proposals_written integer,
    proposals_skipped integer,
    xfw_targets text[],
    dropped_low_conf integer,
    dropped_short_quote integer,
    dropped_hallucinated integer,
    dropped_unknown_ref integer,
    markdown_chars integer,
    paragraph_chars integer,
    candidate_controls integer,
    primary_candidate_controls integer,
    doc_mappings_match_count integer,
    dropped_questionnaire integer,
    skipped_as_toc text,
    crosscheck_disagreements integer,
    crosscheck_confirmed integer,
    crosscheck_unavailable integer,
    workbook_sheets_total integer,
    workbook_sheets_mapped integer,
    workbook_sheets_unmapped integer,
    workbook_unmapped_sheets text,
    workbook_skipped_meta_sheets text,
    distinct_musts_bound integer,
    leaf_musts_in_scope integer,
    yield_ratio_pct integer,
    pass2_leaves_targeted integer,
    pass2_findings integer,
    contract_skip_empty_text integer,
    contract_skip_pure_scaffolding integer,
    contract_skip_mangled_item_id integer,
    contract_skip_unresolvable_control_ref integer,
    templated_zones_scaffolding integer,
    templated_zones_mangled integer,
    dup_of_upload_id text,
    critic_priming_size integer,
    critic_pool_size integer,
    critic_confirmed_raw integer,
    critic_extended_raw integer,
    critic_rejected integer,
    critic_flagged_missing integer,
    critic_findings_kept integer,
    dropped_content_shape integer,
    dropped_semantic_fit integer,
    fingerprint_findings integer,
    fingerprint_covered_leaves integer,
    leaves_dropped_by_classifier integer,
    leaves_fingerprint_hit integer,
    leaves_unfingerprinted_kept integer,
    templated_findings integer,
    templated_xlsx_findings integer,
    templated_edit_zones_total integer,
    templated_edit_zones_bound integer,
    union_from_consensus integer,
    union_from_critic integer,
    union_deduped_count integer,
    CONSTRAINT intake_trace_log_extraction_path_check CHECK ((extraction_path = ANY (ARRAY['full'::text, 'sections'::text, 'manual'::text, 'structured'::text, NULL::text]))),
    CONSTRAINT intake_trace_log_stage_check CHECK ((stage = ANY (ARRAY['read'::text, 'enrich'::text, 'extract'::text, 'write'::text, 'xfw'::text, 'workbook_discovery'::text, 'complete'::text, 'failed'::text]))),
    CONSTRAINT intake_trace_log_stage_status_check CHECK ((stage_status = ANY (ARRAY['ok'::text, 'error'::text, 'skipped'::text, 'manual_review'::text]))),
    CONSTRAINT intake_trace_log_yield_ratio_range CHECK (((yield_ratio_pct IS NULL) OR ((yield_ratio_pct >= 0) AND (yield_ratio_pct <= 100))))
);


--
-- Name: TABLE intake_trace_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.intake_trace_log IS 'Diagnostic log for intake-pipeline QA. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';


--
-- Name: COLUMN intake_trace_log.leaf_musts_in_scope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.leaf_musts_in_scope IS 'Sum of catalog must_contain across target_leaves at extract time. The denominator for yield_ratio_pct.';


--
-- Name: COLUMN intake_trace_log.yield_ratio_pct; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.yield_ratio_pct IS 'distinct_musts_bound / leaf_musts_in_scope * 100, integer 0-100. NULL when target_leaves was unknown (no doc_mappings match).';


--
-- Name: COLUMN intake_trace_log.pass2_leaves_targeted; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.pass2_leaves_targeted IS 'Count of partially-bound leaves fed to _run_pass2. 0 means pass-1 fully bound (or zero-bound) every targeted leaf.';


--
-- Name: COLUMN intake_trace_log.contract_skip_empty_text; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.contract_skip_empty_text IS 'Ship 74''.a — count of ExtractedCandidate.bind() calls this extract stage rejected as EMPTY_TEXT. NULL for non-extract stages.';


--
-- Name: COLUMN intake_trace_log.contract_skip_pure_scaffolding; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.contract_skip_pure_scaffolding IS 'Ship 74''.a — bind() rejections as PURE_SCAFFOLDING (FindingContract.is_scaffolding predicate matched).';


--
-- Name: COLUMN intake_trace_log.contract_skip_mangled_item_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.contract_skip_mangled_item_id IS 'Ship 74''.a — bind() rejections as MANGLED_ITEM_ID (catalog_recognises returned False for the candidate.item_id). Task #606 defence against tenant-mangled markers.';


--
-- Name: COLUMN intake_trace_log.contract_skip_unresolvable_control_ref; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.contract_skip_unresolvable_control_ref IS 'Ship 74''.a — bind() rejections as UNRESOLVABLE_REF (item_control_ref failed to derive a control_ref).';


--
-- Name: COLUMN intake_trace_log.templated_zones_scaffolding; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_zones_scaffolding IS 'Ship 74''.a — Task #606 pre-existing counter, now persisted. Union of PURE_SCAFFOLDING + EMPTY_TEXT contract rejections in templated edit-zone paths (backward-compat mapping preserved by Ship 72''.a extractor.py wiring).';


--
-- Name: COLUMN intake_trace_log.templated_zones_mangled; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_zones_mangled IS 'Ship 74''.a — Task #606 pre-existing counter, now persisted. Number of edit-zone binding markers (`<<MUST item:X>>` /`<<SHOULD item:X>>`) that failed catalog_recognises on this doc — typically indicates tenant edited the marker directly or a mapping YAML typo.';


--
-- Name: COLUMN intake_trace_log.dup_of_upload_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.dup_of_upload_id IS 'Ship 74''.b — canonical upload_id whose content this upload duplicated. Populated only on duplicate-stage rows (markdown/checksum match).';


--
-- Name: COLUMN intake_trace_log.critic_priming_size; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_priming_size IS 'Ship 74''.d — Ship 11''.d critic priming set size at the pass-1 boundary.';


--
-- Name: COLUMN intake_trace_log.critic_pool_size; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_pool_size IS 'Ship 74''.d — Ship 11''.d critic candidate pool size after prefilter.';


--
-- Name: COLUMN intake_trace_log.critic_confirmed_raw; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_confirmed_raw IS 'Ship 74''.d — critic-verifier ``confirmed`` bucket count (pre-filter).';


--
-- Name: COLUMN intake_trace_log.critic_extended_raw; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_extended_raw IS 'Ship 74''.d — critic-verifier ``extended`` bucket count (pre-filter).';


--
-- Name: COLUMN intake_trace_log.critic_rejected; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_rejected IS 'Ship 74''.d — critic-verifier explicit reject count.';


--
-- Name: COLUMN intake_trace_log.critic_flagged_missing; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_flagged_missing IS 'Ship 74''.d — critic-verifier ``flagged_missing_control`` count.';


--
-- Name: COLUMN intake_trace_log.critic_findings_kept; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.critic_findings_kept IS 'Ship 74''.d — findings retained after critic-verifier applies gates.';


--
-- Name: COLUMN intake_trace_log.dropped_content_shape; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.dropped_content_shape IS 'Ship 74''.d — Ship 11''.c content-shape filter drop count (pruned by looks_like_field_or_header MUST-aware predicate).';


--
-- Name: COLUMN intake_trace_log.dropped_semantic_fit; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.dropped_semantic_fit IS 'Ship 74''.d — Ship 11''.d post-critic embedding-cosine semantic-fit gate drop count.';


--
-- Name: COLUMN intake_trace_log.fingerprint_findings; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.fingerprint_findings IS 'Ship 74''.d — deterministic fingerprint-path findings emitted on this doc (peer to `distinct_musts_bound`).';


--
-- Name: COLUMN intake_trace_log.fingerprint_covered_leaves; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.fingerprint_covered_leaves IS 'Ship 74''.d — distinct leaves the fingerprint path bound at least one MUST for.';


--
-- Name: COLUMN intake_trace_log.leaves_dropped_by_classifier; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.leaves_dropped_by_classifier IS 'Ship 74''.d — Ship 11''.c classifier gate: leaves the classifier ruled out before extraction even attempted them.';


--
-- Name: COLUMN intake_trace_log.leaves_fingerprint_hit; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.leaves_fingerprint_hit IS 'Ship 74''.d — leaves the fingerprint-path already covered (no LLM attempt needed).';


--
-- Name: COLUMN intake_trace_log.leaves_unfingerprinted_kept; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.leaves_unfingerprinted_kept IS 'Ship 74''.d — leaves that survived the classifier but had no fingerprint match — the LLM extraction attempts these.';


--
-- Name: COLUMN intake_trace_log.templated_findings; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_findings IS 'Ship 74''.d — templated markdown fast-path findings on this doc.';


--
-- Name: COLUMN intake_trace_log.templated_xlsx_findings; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_xlsx_findings IS 'Ship 74''.d — templated xlsx (Excel round-trip) fast-path findings.';


--
-- Name: COLUMN intake_trace_log.templated_edit_zones_total; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_edit_zones_total IS 'Ship 74''.d — total ▽/△ edit zones detected across the doc.';


--
-- Name: COLUMN intake_trace_log.templated_edit_zones_bound; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.templated_edit_zones_bound IS 'Ship 74''.d — templated edit zones whose contents bound as findings.';


--
-- Name: COLUMN intake_trace_log.union_from_consensus; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.union_from_consensus IS 'Ship 78''.d — number of findings emitted by consensus path on this extract stage. NULL when consensus was disabled (USE_CONSENSUS_EXTRACTION=critic_only) or the union code path didn''t execute (e.g. templated fast-path).';


--
-- Name: COLUMN intake_trace_log.union_from_critic; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.union_from_critic IS 'Ship 78''.d — number of findings emitted by critic-verifier path on this extract stage. NULL when critic was disabled (USE_CONSENSUS_EXTRACTION=consensus_only) or union code path didn''t execute.';


--
-- Name: COLUMN intake_trace_log.union_deduped_count; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.intake_trace_log.union_deduped_count IS 'Ship 78''.d — findings dropped by (control_ref, checklist_item_id) dedup at union merge time. Formula: union_from_consensus + union_from_critic - final_findings_count. Non-zero means both paths hit the same MUST for at least one finding.';


--
-- Name: isms_audits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.isms_audits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    external_ref text,
    audit_type text DEFAULT 'internal'::text NOT NULL,
    audit_date date,
    auditor_name text,
    auditor_org text,
    scope text,
    outcome text,
    certificate_issued boolean DEFAULT false NOT NULL,
    certificate_ref text,
    certificate_expiry date,
    finding_refs text[],
    report_document_id uuid,
    notes text,
    workbook_imported boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    standard_ids text[] NOT NULL,
    CONSTRAINT isms_audits_audit_type_check CHECK ((audit_type = ANY (ARRAY['internal'::text, 'external'::text, 'surveillance'::text, 'recertification'::text]))),
    CONSTRAINT isms_audits_outcome_check CHECK (((outcome = ANY (ARRAY['pass'::text, 'pass_with_ofi'::text, 'fail'::text, 'pending'::text])) OR (outcome IS NULL)))
);


--
-- Name: notification_delivery_attempt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notification_delivery_attempt (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    notification_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    channel_id uuid NOT NULL,
    channel_kind text NOT NULL,
    endpoint text NOT NULL,
    attempted_at timestamp with time zone DEFAULT now() NOT NULL,
    delivered_at timestamp with time zone,
    error_type text,
    error_detail text,
    latency_ms integer,
    retry_count integer DEFAULT 0 NOT NULL
);


--
-- Name: TABLE notification_delivery_attempt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.notification_delivery_attempt IS 'One row per (notification, channel, attempt). Success = delivered_at populated. Failed rows drive backoff retry.';


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    user_id uuid,
    target_role text,
    type text NOT NULL,
    severity text DEFAULT 'info'::text NOT NULL,
    title text NOT NULL,
    body text NOT NULL,
    action_url text,
    source_table text,
    source_id uuid,
    delivered_at timestamp with time zone,
    read_at timestamp with time zone,
    dismissed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'platform'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT notifications_severity_check CHECK ((severity = ANY (ARRAY['info'::text, 'warning'::text, 'urgent'::text, 'critical'::text])))
);


--
-- Name: posture_assertions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_assertions (
    id bigint NOT NULL,
    tenant_id uuid NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    source text NOT NULL,
    finding text NOT NULL,
    gap_description text,
    confidence text,
    set_by text NOT NULL,
    set_at timestamp with time zone DEFAULT now() NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    superseded_at timestamp with time zone,
    superseded_by_id bigint,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT posture_assertions_finding_check CHECK ((finding = ANY (ARRAY['NC'::text, 'OFI'::text, 'Comply'::text, 'N/A'::text, 'Not assessed'::text]))),
    CONSTRAINT posture_assertions_source_check CHECK ((source = ANY (ARRAY['tenant'::text, 'assessor'::text, 'engine'::text]))),
    CONSTRAINT posture_assertions_status_check CHECK ((status = ANY (ARRAY['active'::text, 'pending'::text, 'superseded'::text]))),
    CONSTRAINT posture_assertions_superseded_consistency CHECK (((status = 'superseded'::text) = (superseded_at IS NOT NULL)))
);


--
-- Name: posture_assertions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.posture_assertions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posture_assertions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.posture_assertions_id_seq OWNED BY public.posture_assertions.id;


--
-- Name: posture_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    finding text NOT NULL,
    confidence text NOT NULL,
    gap_description text,
    action_required text,
    source text NOT NULL,
    chat_session_id text,
    established_via text,
    changed_by uuid,
    changed_by_role text,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
)
PARTITION BY RANGE (created_at);


--
-- Name: posture_history_2025; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_history_2025 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    finding text NOT NULL,
    confidence text NOT NULL,
    gap_description text,
    action_required text,
    source text NOT NULL,
    chat_session_id text,
    established_via text,
    changed_by uuid,
    changed_by_role text,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: posture_history_2026; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_history_2026 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    finding text NOT NULL,
    confidence text NOT NULL,
    gap_description text,
    action_required text,
    source text NOT NULL,
    chat_session_id text,
    established_via text,
    changed_by uuid,
    changed_by_role text,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: posture_history_2027; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_history_2027 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    finding text NOT NULL,
    confidence text NOT NULL,
    gap_description text,
    action_required text,
    source text NOT NULL,
    chat_session_id text,
    established_via text,
    changed_by uuid,
    changed_by_role text,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: posture_history_2028; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_history_2028 (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    finding text NOT NULL,
    confidence text NOT NULL,
    gap_description text,
    action_required text,
    source text NOT NULL,
    chat_session_id text,
    established_via text,
    changed_by uuid,
    changed_by_role text,
    confirmed_by uuid,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    source_authority text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: posture_must_bridge_coverage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_must_bridge_coverage (
    id bigint NOT NULL,
    tenant_id uuid NOT NULL,
    target_must_id text NOT NULL,
    target_control_ref text NOT NULL,
    target_standard_id text NOT NULL,
    target_role text NOT NULL,
    source_must_id text NOT NULL,
    source_control_ref text NOT NULL,
    source_standard_id text NOT NULL,
    source_role text NOT NULL,
    edge_type text NOT NULL,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT posture_must_bridge_coverage_edge_type_check CHECK ((edge_type = ANY (ARRAY['IMPLEMENTS'::text, 'SUPPORTS'::text, 'ENABLES'::text, 'GOVERNANCE'::text]))),
    CONSTRAINT posture_must_bridge_coverage_source_role_check CHECK ((source_role = ANY (ARRAY['PROGRAM'::text, 'EXTENSION'::text, 'OBLIGATION'::text, 'OTHER'::text]))),
    CONSTRAINT posture_must_bridge_coverage_target_role_check CHECK ((target_role = ANY (ARRAY['PROGRAM'::text, 'EXTENSION'::text, 'OBLIGATION'::text, 'OTHER'::text])))
);


--
-- Name: posture_must_bridge_coverage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.posture_must_bridge_coverage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posture_must_bridge_coverage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.posture_must_bridge_coverage_id_seq OWNED BY public.posture_must_bridge_coverage.id;


--
-- Name: posture_must_verdicts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_must_verdicts (
    id bigint NOT NULL,
    tenant_id uuid NOT NULL,
    must_id text NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    satisfied boolean NOT NULL,
    stale boolean DEFAULT false NOT NULL,
    partial boolean DEFAULT false NOT NULL,
    reason text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    framework_role text,
    CONSTRAINT posture_must_verdicts_framework_role_check CHECK (((framework_role IS NULL) OR (framework_role = ANY (ARRAY['PROGRAM'::text, 'EXTENSION'::text, 'OBLIGATION'::text, 'OTHER'::text]))))
);


--
-- Name: posture_must_verdicts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.posture_must_verdicts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posture_must_verdicts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.posture_must_verdicts_id_seq OWNED BY public.posture_must_verdicts.id;


--
-- Name: posture_pending; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_pending (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    control_id uuid NOT NULL,
    proposed_finding text NOT NULL,
    proposed_gap text,
    proposed_action text,
    proposed_confidence text DEFAULT 'medium'::text NOT NULL,
    extraction_source text,
    extraction_rationale text,
    status text DEFAULT 'pending'::text NOT NULL,
    client_note text,
    resolved_by uuid,
    resolved_at timestamp with time zone,
    chat_session_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'compliance'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT posture_pending_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'confirmed'::text, 'rejected'::text, 'modified'::text])))
);


--
-- Name: posture_status_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posture_status_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    posture_id uuid,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    status_before text,
    status_after text NOT NULL,
    source text NOT NULL,
    source_upload_id uuid,
    evidence_citation text,
    confidence text,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    change_kind text DEFAULT 'extraction'::text NOT NULL,
    CONSTRAINT posture_status_log_change_kind_check CHECK ((change_kind = ANY (ARRAY['extraction'::text, 'engine'::text, 'assessor'::text, 'acknowledgement'::text, 'revert'::text])))
);


--
-- Name: TABLE posture_status_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.posture_status_log IS 'Compliance-load-bearing audit trail of posture status changes. Append-only by contract for arioncomply_app (INSERT + SELECT only). Tenant FK is NO ACTION so tenant deletion requires explicit erasure flow. Do NOT grant UPDATE or DELETE without designing an erasure-with-provenance mechanism.';


--
-- Name: ref_prefixes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ref_prefixes (
    prefix text NOT NULL,
    entity_type text NOT NULL,
    table_name text NOT NULL,
    description text
);


--
-- Name: ref_sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ref_sequences (
    tenant_id uuid NOT NULL,
    prefix text NOT NULL,
    next_seq integer DEFAULT 1 NOT NULL
);


--
-- Name: remediation_evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.remediation_evidence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    document_id uuid,
    note text,
    submitted_by uuid,
    submitted_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: remediation_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.remediation_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    control_id uuid NOT NULL,
    title text NOT NULL,
    description text,
    status text DEFAULT 'draft'::text NOT NULL,
    owner uuid,
    target_date date,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    risk_id uuid,
    risk_ref text,
    residual_risk text,
    residual_risk_level integer,
    treatment_option text,
    review_date date,
    effectiveness_review text,
    workbook_imported boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT remediation_plans_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'active'::text, 'completed'::text, 'cancelled'::text])))
);


--
-- Name: remediation_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.remediation_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    title text NOT NULL,
    description text,
    status text DEFAULT 'open'::text NOT NULL,
    owner uuid,
    due_date date,
    completed_at timestamp with time zone,
    effort_hours numeric(5,1),
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT remediation_tasks_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_progress'::text, 'done'::text, 'skipped'::text])))
);


--
-- Name: request_trace_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.request_trace_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    request_id text NOT NULL,
    tenant_id uuid NOT NULL,
    query_text text NOT NULL,
    classifier_type text NOT NULL,
    taxonomy_type text NOT NULL,
    handler_name text NOT NULL,
    strategy text NOT NULL,
    topic_ref text,
    policy_posture boolean DEFAULT true NOT NULL,
    policy_vector boolean DEFAULT true NOT NULL,
    policy_graph boolean DEFAULT true NOT NULL,
    policy_doc_inv boolean DEFAULT false NOT NULL,
    policy_short_circuit boolean DEFAULT false NOT NULL,
    node_ids_built integer DEFAULT 0 NOT NULL,
    nodes_primary integer DEFAULT 0 NOT NULL,
    nodes_secondary integer DEFAULT 0 NOT NULL,
    vector_hits integer DEFAULT 0 NOT NULL,
    doc_contexts integer DEFAULT 0 NOT NULL,
    posture_ids_used text[],
    vector_top_scores jsonb,
    posture_total integer DEFAULT 0 NOT NULL,
    posture_nc integer DEFAULT 0 NOT NULL,
    posture_ofi integer DEFAULT 0 NOT NULL,
    posture_confirmed integer DEFAULT 0 NOT NULL,
    posture_draft integer DEFAULT 0 NOT NULL,
    short_circuit boolean DEFAULT false NOT NULL,
    answer_source text DEFAULT 'llm'::text NOT NULL,
    neo4j_ms integer DEFAULT 0 NOT NULL,
    vector_ms integer DEFAULT 0 NOT NULL,
    postgres_ms integer DEFAULT 0 NOT NULL,
    total_ms integer DEFAULT 0 NOT NULL,
    error_type text,
    error_hint text,
    traced_at timestamp with time zone DEFAULT now() NOT NULL,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: retention_policies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.retention_policies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    retention_class text NOT NULL,
    table_name text,
    retain_years integer DEFAULT 0 NOT NULL,
    retain_days integer DEFAULT 0 NOT NULL,
    anonymise_after_years integer,
    auto_purge boolean DEFAULT false NOT NULL,
    legal_basis text NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: risks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.risks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    external_ref text NOT NULL,
    asset_id uuid,
    asset_ref text,
    asset_name text,
    interested_party text,
    threat text,
    vulnerability text,
    likelihood integer,
    impact integer,
    risk_score integer,
    risk_owner_text text,
    risk_owner uuid,
    treatment_option text,
    treatment_action text,
    implementation_date date,
    residual_risk_level integer,
    treatment_status text,
    review_date date,
    effectiveness_review text,
    workbook_imported boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    control_refs text[] DEFAULT '{}'::text[],
    treatment_rationale text,
    resources_required text,
    performance_indicators text[],
    constraints text,
    reporting_cadence text,
    CONSTRAINT risks_impact_check CHECK (((impact >= 1) AND (impact <= 5))),
    CONSTRAINT risks_likelihood_check CHECK (((likelihood >= 1) AND (likelihood <= 5))),
    CONSTRAINT risks_residual_risk_level_check CHECK (((residual_risk_level >= 1) AND (residual_risk_level <= 25))),
    CONSTRAINT risks_treatment_option_check CHECK (((treatment_option = ANY (ARRAY['Mitigate'::text, 'Accept'::text, 'Transfer'::text, 'Avoid'::text])) OR (treatment_option IS NULL))),
    CONSTRAINT risks_treatment_status_check CHECK (((treatment_status = ANY (ARRAY['open'::text, 'in_progress'::text, 'implemented'::text, 'accepted'::text])) OR (treatment_status IS NULL)))
);


--
-- Name: COLUMN risks.treatment_rationale; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.risks.treatment_rationale IS '27005:2022 §8.6.1 — rationale for the selected treatment option, including expected benefits.';


--
-- Name: COLUMN risks.resources_required; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.risks.resources_required IS '27005:2022 §8.6.1 — resources required for implementation (budget / people / infrastructure).';


--
-- Name: COLUMN risks.performance_indicators; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.risks.performance_indicators IS '27005:2022 §8.6.1 — performance indicators (KPIs) that will demonstrate the treatment is effective.';


--
-- Name: COLUMN risks.constraints; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.risks.constraints IS '27005:2022 §8.6.1 — dependencies, timing gates, or other constraints on treatment execution.';


--
-- Name: COLUMN risks.reporting_cadence; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.risks.reporting_cadence IS '27005:2022 §8.6.1 — how often status is reported to risk owner and management.';


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    can_write_posture boolean DEFAULT false NOT NULL,
    can_write_incidents boolean DEFAULT false NOT NULL,
    can_write_documents boolean DEFAULT false NOT NULL,
    can_manage_users boolean DEFAULT false NOT NULL,
    can_view_all boolean DEFAULT false NOT NULL,
    is_arion_staff boolean DEFAULT false NOT NULL
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: standard_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standard_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id text NOT NULL,
    target_id text NOT NULL,
    relationship text NOT NULL,
    mapping_source text,
    coverage text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT standard_relationships_coverage_check CHECK (((coverage = ANY (ARRAY['full'::text, 'partial'::text])) OR (coverage IS NULL))),
    CONSTRAINT standard_relationships_relationship_check CHECK ((relationship = ANY (ARRAY['extends'::text, 'maps_to'::text, 'requires'::text, 'satisfies'::text, 'references'::text, 'implements'::text])))
);


--
-- Name: standards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standards (
    id text NOT NULL,
    family text NOT NULL,
    version text NOT NULL,
    full_name text NOT NULL,
    short_name text NOT NULL,
    standard_type text NOT NULL,
    certifiable boolean DEFAULT false NOT NULL,
    jurisdiction text,
    description text,
    annex_mapping text,
    loaded_in_graph boolean DEFAULT false NOT NULL,
    node_count integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    role text NOT NULL,
    subject text[] DEFAULT ARRAY[]::text[] NOT NULL,
    scope_type text DEFAULT 'org_wide'::text NOT NULL,
    mandate_source text,
    CONSTRAINT standards_mandate_source_chk CHECK (((mandate_source IS NULL) OR (mandate_source = ANY (ARRAY['voluntary'::text, 'attestation'::text, 'legal'::text, 'contractual'::text])))),
    CONSTRAINT standards_role_chk CHECK ((role = ANY (ARRAY['program'::text, 'extension'::text, 'obligation'::text, 'guidance'::text]))),
    CONSTRAINT standards_scope_type_chk CHECK ((scope_type = ANY (ARRAY['org_wide'::text, 'data_type_scoped'::text, 'sector_scoped'::text, 'system_scoped'::text]))),
    CONSTRAINT standards_standard_type_check CHECK ((standard_type = ANY (ARRAY['management_system'::text, 'regulation'::text, 'framework'::text, 'code_of_practice'::text])))
);


--
-- Name: sweep_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sweep_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tick_id uuid NOT NULL,
    work_type text NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    status text NOT NULL,
    items_scanned integer,
    items_acted_on integer,
    items_error integer,
    detail jsonb DEFAULT '{}'::jsonb NOT NULL,
    error_type text,
    error_detail text,
    CONSTRAINT sweep_log_status_check CHECK ((status = ANY (ARRAY['running'::text, 'completed'::text, 'failed'::text]))),
    CONSTRAINT sweep_log_work_type_check CHECK ((work_type = ANY (ARRAY['fact_recompute'::text, 'overdue_followups'::text, 'freshness_expiry'::text, 'notification_delivery'::text, 'engine_kick'::text, 'cite_verification_overdue'::text, 'api_key_expiring'::text, 'notification_retention'::text, 'risk_register_notify'::text, 'posture_refresh'::text, 'cite_attestation_retention'::text, 'other'::text])))
);


--
-- Name: TABLE sweep_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sweep_log IS 'Sweep scheduler audit trail — one row per (tick, work_type). Fed by rag.scheduler.tick. Not tenant-scoped: tick runs across all tenants in one call.';


--
-- Name: COLUMN sweep_log.work_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sweep_log.work_type IS 'Sweep tick work_type. Added in Ship 88''.a: workbook_link_resolver — walks workbook_hyperlink_followup rows with status=''pending'', resolves URL basename against client_documents.original_filename (strict basename+ext match), promotes to satisfied when target has present findings on same MUST or to linked_doc_missing when basename unmatched.';


--
-- Name: tabular_evidence_rows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tabular_evidence_rows (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL,
    leaf_id text NOT NULL,
    row_index integer NOT NULL,
    column_values jsonb DEFAULT '{}'::jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    extracted_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tabular_evidence_rows_row_index_nonneg CHECK ((row_index >= 0))
);


--
-- Name: TABLE tabular_evidence_rows; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tabular_evidence_rows IS 'Per-row capture of tabular template content. Sibling to document_findings; engine semantics unchanged.';


--
-- Name: COLUMN tabular_evidence_rows.column_values; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tabular_evidence_rows.column_values IS 'Sparse JSONB map: {item_id: cell_text}. Empty cells omitted (not "").';


--
-- Name: templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.templates (
    leaf_id text NOT NULL,
    template_version integer DEFAULT 1 NOT NULL,
    body_md text NOT NULL,
    source_file text NOT NULL,
    must_count integer DEFAULT 0 NOT NULL,
    should_count integer DEFAULT 0 NOT NULL,
    last_loaded_at timestamp with time zone DEFAULT now() NOT NULL,
    last_loaded_by text,
    CONSTRAINT templates_counts_nonneg CHECK (((must_count >= 0) AND (should_count >= 0))),
    CONSTRAINT templates_version_ge_1 CHECK ((template_version >= 1))
);


--
-- Name: TABLE templates; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.templates IS 'Markdown template skeletons per EvidenceRequirement leaf; canonical source is db/templates/*.md filesystem; this table is the runtime-serving copy.';


--
-- Name: COLUMN templates.leaf_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.templates.leaf_id IS 'EvidenceRequirement.id — e.g. req:A.5.15:access_control_policy';


--
-- Name: COLUMN templates.template_version; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.templates.template_version IS 'Auto-gen scaffolds=1; hand-refined=2+. Generator preserves files with version >= 2.';


--
-- Name: COLUMN templates.must_count; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.templates.must_count IS 'Count of <<MUST item:X>> markers in body; loader enforces equality with leaf.must_contain length.';


--
-- Name: tenant_cascade_override; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_cascade_override (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    override_kind text NOT NULL,
    event_type text NOT NULL,
    target_requirement_id text,
    reason text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    CONSTRAINT tenant_cascade_override_consistency_chk CHECK ((((override_kind = 'mute_event'::text) AND (target_requirement_id IS NULL)) OR ((override_kind = 'mute_event_target'::text) AND (target_requirement_id IS NOT NULL)))),
    CONSTRAINT tenant_cascade_override_kind_chk CHECK ((override_kind = ANY (ARRAY['mute_event'::text, 'mute_event_target'::text])))
);


--
-- Name: TABLE tenant_cascade_override; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tenant_cascade_override IS 'Per-tenant cascade-behaviour overrides. Engine consults these before writing triggered_implication rows; matched rows suppress + log to cascade_suppression_log.';


--
-- Name: tenant_standards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_standards (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    standard_id text NOT NULL,
    status text DEFAULT 'implementing'::text NOT NULL,
    cert_body text,
    cert_ref text,
    cert_date date,
    cert_expiry date,
    next_audit_date date,
    soa_version text,
    soa_date date,
    scope_description text,
    enrolled_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'platform'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT tenant_standards_status_check CHECK ((status = ANY (ARRAY['implementing'::text, 'implemented'::text, 'certified'::text, 'surveillance'::text, 'lapsed'::text])))
);


--
-- Name: tenant_evaluation_scope; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.tenant_evaluation_scope AS
 WITH direct AS (
         SELECT ts.tenant_id,
            ts.standard_id,
            ts.status,
            s.standard_type,
            s.certifiable,
            'direct'::text AS scope_source,
            ts.standard_id AS via_standard,
            NULL::text AS relationship
           FROM (public.tenant_standards ts
             JOIN public.standards s ON ((s.id = ts.standard_id)))
          WHERE (ts.status = ANY (ARRAY['implementing'::text, 'implemented'::text, 'certified'::text, 'surveillance'::text]))
        ), inferred AS (
         SELECT d.tenant_id,
            sr.target_id AS standard_id,
            d.status,
            s.standard_type,
            s.certifiable,
            'inferred'::text AS scope_source,
            d.standard_id AS via_standard,
            sr.relationship
           FROM ((direct d
             JOIN public.standard_relationships sr ON ((sr.source_id = d.standard_id)))
             JOIN public.standards s ON ((s.id = sr.target_id)))
          WHERE (sr.relationship = ANY (ARRAY['maps_to'::text, 'satisfies'::text]))
        ), xfw_inherited AS (
         SELECT d.tenant_id,
            sr.target_id AS standard_id,
            d.status,
            s.standard_type,
            s.certifiable,
            'xfw_inherited'::text AS scope_source,
            d.standard_id AS via_standard,
            sr.relationship
           FROM ((direct d
             JOIN public.standard_relationships sr ON ((sr.source_id = d.standard_id)))
             JOIN public.standards s ON ((s.id = sr.target_id)))
          WHERE ((sr.relationship = 'implements'::text) AND (sr.target_id <> d.standard_id) AND (NOT (EXISTS ( SELECT 1
                   FROM public.standard_relationships sr2
                  WHERE ((sr2.source_id = d.standard_id) AND (sr2.target_id = sr.target_id) AND (sr2.relationship = ANY (ARRAY['maps_to'::text, 'satisfies'::text])))))) AND (NOT (EXISTS ( SELECT 1
                   FROM public.tenant_standards ts2
                  WHERE ((ts2.tenant_id = d.tenant_id) AND (ts2.standard_id = sr.target_id) AND (ts2.status = ANY (ARRAY['implementing'::text, 'implemented'::text, 'certified'::text, 'surveillance'::text])))))))
        )
 SELECT direct.tenant_id,
    direct.standard_id,
    direct.status,
    direct.standard_type,
    direct.certifiable,
    direct.scope_source,
    direct.via_standard,
    direct.relationship
   FROM direct
UNION ALL
 SELECT inferred.tenant_id,
    inferred.standard_id,
    inferred.status,
    inferred.standard_type,
    inferred.certifiable,
    inferred.scope_source,
    inferred.via_standard,
    inferred.relationship
   FROM inferred
UNION ALL
 SELECT xfw_inherited.tenant_id,
    xfw_inherited.standard_id,
    xfw_inherited.status,
    xfw_inherited.standard_type,
    xfw_inherited.certifiable,
    xfw_inherited.scope_source,
    xfw_inherited.via_standard,
    xfw_inherited.relationship
   FROM xfw_inherited;


--
-- Name: tenant_evidence_gaps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_evidence_gaps (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    control_id text NOT NULL,
    control_ref text NOT NULL,
    standard_id text NOT NULL,
    leaf_id text NOT NULL,
    role text NOT NULL,
    evidence_type text NOT NULL,
    gap_summary text NOT NULL,
    gap_items text[] DEFAULT '{}'::text[] NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    rationale text,
    acknowledged_by text,
    acknowledged_at timestamp with time zone,
    first_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tenant_evidence_gaps_status_check CHECK ((status = ANY (ARRAY['open'::text, 'acknowledged'::text, 'resolved'::text])))
);


--
-- Name: tenant_external_system; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_external_system (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    system_name text NOT NULL,
    system_url text,
    owner_user_id uuid,
    default_cadence_days integer DEFAULT 365 NOT NULL,
    covers_evidence_types text[] DEFAULT ARRAY[]::text[] NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    CONSTRAINT tenant_external_system_cadence_positive CHECK (((default_cadence_days >= 1) AND (default_cadence_days <= 3650)))
);


--
-- Name: TABLE tenant_external_system; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tenant_external_system IS 'Per-tenant registry of external systems used as compliance evidence sources. One row per (tenant, system). Many cites reference each row.';


--
-- Name: COLUMN tenant_external_system.covers_evidence_types; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tenant_external_system.covers_evidence_types IS 'Evidence types this system is offered for in cite-source pickers. Empty = offered for all cite-acceptable types.';


--
-- Name: tenant_must_overrides; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_must_overrides (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    must_id text NOT NULL,
    applies boolean DEFAULT false NOT NULL,
    reason text,
    set_by uuid,
    set_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: tenant_notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_notification (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    kind text NOT NULL,
    title text NOT NULL,
    body text,
    severity text DEFAULT 'info'::text NOT NULL,
    related_entity_kind text,
    related_entity_id uuid,
    related_control_ref text,
    related_event_type text,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    read_at timestamp with time zone,
    dismissed_at timestamp with time zone,
    CONSTRAINT tenant_notification_kind_check CHECK ((kind = ANY (ARRAY['implication_overdue'::text, 'followup_overdue'::text, 'threshold_crossed'::text, 'cascade_blocked'::text, 'auto_resolved'::text, 'freshness_expiry'::text, 'nc_surfaced'::text, 'upload_processed'::text, 'stage2_proposal_ready'::text, 'upload_failed'::text, 'cite_verification_overdue'::text, 'posture_flip_to_comply'::text, 'api_key_expiring'::text, 'risk_added'::text, 'risk_treatment_overdue'::text, 'residual_above_threshold'::text, 'risk_review_due'::text]))),
    CONSTRAINT tenant_notification_severity_chk CHECK ((severity = ANY (ARRAY['critical'::text, 'high'::text, 'medium'::text, 'low'::text, 'info'::text])))
);


--
-- Name: TABLE tenant_notification; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tenant_notification IS 'Per-tenant in-app notifications. Cascade write sites emit rows; frontend bell + inbox reads. Active-row partial unique prevents per-entity duplicate spam.';


--
-- Name: COLUMN tenant_notification.kind; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tenant_notification.kind IS 'Notification category. Kind added in Ship 88''.a (2026-08-20): workbook_link_unresolved — a workbook cell hyperlinks to an external document whose basename does not match any client_documents.original_filename. Producer: Ship 88''.c resolver sweep.';


--
-- Name: tenant_notification_channel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_notification_channel (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    channel_kind text NOT NULL,
    endpoint text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    min_severity text DEFAULT 'medium'::text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT nc_kind_check CHECK ((channel_kind = ANY (ARRAY['email'::text, 'slack'::text, 'webhook'::text, 'sms'::text]))),
    CONSTRAINT nc_severity_check CHECK ((min_severity = ANY (ARRAY['info'::text, 'low'::text, 'medium'::text, 'high'::text, 'critical'::text])))
);


--
-- Name: TABLE tenant_notification_channel; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tenant_notification_channel IS 'Per-tenant outbound delivery configuration. Delivery worker iterates active channels for each undelivered tenant_notification.';


--
-- Name: tenant_profile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_profile (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    profile_key text NOT NULL,
    profile_value text DEFAULT ''::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_by uuid,
    CONSTRAINT tenant_profile_key_format CHECK ((profile_key ~ '^[a-z][a-z0-9_]*$'::text))
);


--
-- Name: TABLE tenant_profile; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tenant_profile IS 'Key/value store for template-substitution placeholders. Keyed by tenant_id + profile_key (lowercase_with_underscores).';


--
-- Name: COLUMN tenant_profile.profile_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tenant_profile.profile_key IS 'Placeholder name with the <<>> wrapping removed and lowercased: <<CEO_NAME>> → ceo_name';


--
-- Name: tenant_source_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant_source_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    source_id text NOT NULL,
    source_type text NOT NULL,
    display_name text NOT NULL,
    connection_url text,
    auth_type text,
    secrets_ref text,
    status text DEFAULT 'active'::text NOT NULL,
    last_synced_at timestamp with time zone,
    last_error text,
    record_count integer DEFAULT 0 NOT NULL,
    connected_by uuid,
    connected_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'platform'::text NOT NULL,
    purge_after timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tenant_source_registry_auth_type_check CHECK (((auth_type IS NULL) OR (auth_type = ANY (ARRAY['oauth2'::text, 'api_key'::text, 'basic'::text, 'none'::text])))),
    CONSTRAINT tenant_source_registry_source_type_check CHECK ((source_type = ANY (ARRAY['internal'::text, 'document'::text, 'api'::text, 'manual'::text]))),
    CONSTRAINT tenant_source_registry_status_check CHECK ((status = ANY (ARRAY['active'::text, 'pending_confirmation'::text, 'disabled'::text, 'error'::text])))
);


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    sector text,
    country text DEFAULT 'GB'::text,
    timezone text DEFAULT 'Europe/London'::text,
    subscription text DEFAULT 'free'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    short_code text,
    industry text,
    employee_count integer,
    has_physical_premises boolean DEFAULT true,
    does_software_development boolean DEFAULT false,
    cloud_only boolean DEFAULT false,
    onboarding_status text DEFAULT 'registered'::text,
    CONSTRAINT tenants_onboarding_status_check CHECK ((onboarding_status = ANY (ARRAY['registered'::text, 'assessed'::text, 'active'::text]))),
    CONSTRAINT tenants_subscription_check CHECK ((subscription = ANY (ARRAY['free'::text, 'starter'::text, 'professional'::text, 'enterprise'::text])))
);


--
-- Name: topic_leaves; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topic_leaves (
    topic_slug text NOT NULL,
    leaf_id text NOT NULL,
    role text NOT NULL,
    workflow_order smallint DEFAULT 100 NOT NULL,
    role_note text
);


--
-- Name: topics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.topics (
    slug text NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    primary_framework text NOT NULL,
    auditor_expects text,
    display_order smallint DEFAULT 100 NOT NULL,
    source_file text NOT NULL,
    last_loaded_at timestamp with time zone DEFAULT now() NOT NULL,
    last_loaded_by text
);


--
-- Name: triggered_implication; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.triggered_implication (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    source_verification_id uuid NOT NULL,
    source_event_type text NOT NULL,
    cascade_path jsonb DEFAULT '[]'::jsonb NOT NULL,
    cascade_depth integer DEFAULT 0 NOT NULL,
    target_control_ref text NOT NULL,
    target_standard_id text NOT NULL,
    target_requirement_id text NOT NULL,
    expected_action text DEFAULT 'evidence_required'::text NOT NULL,
    fired_at timestamp with time zone DEFAULT now() NOT NULL,
    due_date timestamp with time zone,
    status text DEFAULT 'pending'::text NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by uuid,
    resolved_evidence_kind text,
    resolved_evidence_id uuid,
    dismissed_reason text,
    rationale text,
    deadline_string text,
    scope_kind text,
    clock_anchor text DEFAULT 'verified_at'::text NOT NULL,
    CONSTRAINT triggered_implication_clock_anchor_chk CHECK ((clock_anchor = ANY (ARRAY['verified_at'::text, 'occurred_at'::text]))),
    CONSTRAINT triggered_implication_depth_chk CHECK (((cascade_depth >= 0) AND (cascade_depth <= 4))),
    CONSTRAINT triggered_implication_expected_action_chk CHECK ((expected_action = ANY (ARRAY['evidence_required'::text, 'review_required'::text, 'attestation_required'::text]))),
    CONSTRAINT triggered_implication_resolution_consistent CHECK ((((status = 'pending'::text) AND (resolved_at IS NULL) AND (dismissed_reason IS NULL)) OR ((status = 'satisfied'::text) AND (resolved_at IS NOT NULL)) OR ((status = 'dismissed'::text) AND (resolved_at IS NOT NULL) AND (dismissed_reason IS NOT NULL) AND (length(TRIM(BOTH FROM dismissed_reason)) > 0)))),
    CONSTRAINT triggered_implication_status_chk CHECK ((status = ANY (ARRAY['pending'::text, 'satisfied'::text, 'dismissed'::text])))
);


--
-- Name: TABLE triggered_implication; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.triggered_implication IS 'Per-tenant cascade-engine output. One row per (downstream event, target obligation) pair fired by a verification.';


--
-- Name: COLUMN triggered_implication.cascade_path; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.triggered_implication.cascade_path IS 'Ordered list of event_types in the emission chain. Length 1 = direct from structured_events. Up to 4 per the depth cap (P9 from cascade meditation).';


--
-- Name: COLUMN triggered_implication.due_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.triggered_implication.due_date IS 'verified_at + parsed(deadline). NULL when the trigger edge has no headline deadline. The reader treats now() > due_date AND status=pending as overdue.';


--
-- Name: COLUMN triggered_implication.dismissed_reason; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.triggered_implication.dismissed_reason IS 'Required when status=dismissed (CHECK enforced). Auditor-grade explanation of why this implication was deemed inapplicable / already-addressed / superseded.';


--
-- Name: COLUMN triggered_implication.scope_kind; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.triggered_implication.scope_kind IS 'Set when the implication was fired by an EXPANDS_SCOPE edge (e.g. facility_added). Identifies which scope dimension expanded so the UI can render "re-evaluate for new site".';


--
-- Name: COLUMN triggered_implication.clock_anchor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.triggered_implication.clock_anchor IS 'Which timestamp anchored the deadline clock for this implication: verified_at (default) or occurred_at (tenant-supplied event-time, for processor-discovered breach and similar scenarios where awareness postdates occurrence).';


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    role_id integer NOT NULL,
    granted_by uuid,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    revoked_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'personal_data'::text NOT NULL,
    purge_after timestamp with time zone
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    email text NOT NULL,
    full_name text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_login_at timestamp with time zone,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'personal_data'::text NOT NULL,
    purge_after timestamp with time zone,
    anonymised_at timestamp with time zone
);


--
-- Name: v_audit_evidence; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_audit_evidence AS
 SELECT pc.tenant_id,
    pc.standard_id,
    pc.control_ref,
    pc.node_id,
    pc.finding,
    pc.confidence,
    pc.gap_description,
    pc.action_required,
    pc.evidence_present,
    pc.remediation_status,
    pc.target_date,
    pc.source,
    pc.assessed_at,
    cd.filename,
    cd.version AS document_version,
    cd.approved_by,
    cd.approval_date,
    df.status AS evidence_status,
    df.excerpt AS evidence_excerpt,
    df.section_number,
    df.page_number,
    df.requirement_text,
    df.gdpr_required,
    df.confirmed_by AS evidence_confirmed_by,
    df.confirmed_at AS evidence_confirmed_at
   FROM ((public.posture_controls pc
     LEFT JOIN public.document_findings df ON (((df.tenant_id = pc.tenant_id) AND (df.control_ref = pc.control_ref) AND (df.status = 'present'::text) AND (df.confirmed_at IS NOT NULL))))
     LEFT JOIN public.client_documents cd ON (((cd.id = df.document_id) AND (cd.is_current = true))));


--
-- Name: v_incidents_open; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_incidents_open AS
 SELECT id,
    tenant_id,
    title,
    description,
    status,
    severity,
    occurred_at,
    reported_at,
    deadline_at,
    notified_at,
    closed_at,
    affected_count_approx,
    affected_categories,
    affected_countries,
    created_by,
    chat_session_id,
    created_at,
    updated_at,
    expires_at,
    external_ref,
    asset_ref,
    pii_involved,
    authority_notified,
    data_subjects_notified,
    lessons_learned,
    pii_restoration_auth_by,
    actions_taken,
    evidence_collected,
    workbook_imported,
    platform_ref,
    is_active,
    deleted_at,
    deleted_by,
    deletion_reason,
    retention_class,
    purge_after,
        CASE
            WHEN (deadline_at IS NULL) THEN NULL::numeric
            ELSE (EXTRACT(epoch FROM (deadline_at - now())) / (3600)::numeric)
        END AS hours_remaining,
        CASE
            WHEN (deadline_at IS NULL) THEN 'no_deadline'::text
            WHEN (deadline_at < now()) THEN 'overdue'::text
            WHEN (deadline_at < (now() + '12:00:00'::interval)) THEN 'critical'::text
            WHEN (deadline_at < (now() + '48:00:00'::interval)) THEN 'urgent'::text
            WHEN (deadline_at < (now() + '7 days'::interval)) THEN 'soon'::text
            ELSE 'on_track'::text
        END AS urgency
   FROM public.incidents i
  WHERE (status = ANY (ARRAY['open'::text, 'in_progress'::text]));


--
-- Name: v_intake_runs; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_intake_runs AS
 SELECT trace_id,
    tenant_id,
    upload_id,
    filename,
    max(
        CASE
            WHEN (stage = 'enrich'::text) THEN doc_type
            ELSE NULL::text
        END) AS doc_type,
    max(
        CASE
            WHEN (stage = 'enrich'::text) THEN (standard_ids)::text
            ELSE NULL::text
        END) AS standard_ids,
    max(
        CASE
            WHEN (stage = 'enrich'::text) THEN extraction_path
            ELSE NULL::text
        END) AS extraction_path,
    max(
        CASE
            WHEN (stage = 'read'::text) THEN token_estimate
            ELSE NULL::integer
        END) AS token_estimate,
    max(
        CASE
            WHEN (stage = 'extract'::text) THEN findings_kept
            ELSE NULL::integer
        END) AS findings_extracted,
    max(
        CASE
            WHEN (stage = 'write'::text) THEN findings_written
            ELSE NULL::integer
        END) AS findings_written,
    max(
        CASE
            WHEN (stage = 'write'::text) THEN posture_created
            ELSE NULL::integer
        END) AS posture_created,
    max(
        CASE
            WHEN (stage = 'write'::text) THEN posture_updated
            ELSE NULL::integer
        END) AS posture_updated,
    max(
        CASE
            WHEN (stage = 'write'::text) THEN posture_skipped
            ELSE NULL::integer
        END) AS posture_skipped,
    max(
        CASE
            WHEN (stage = 'xfw'::text) THEN proposals_written
            ELSE NULL::integer
        END) AS proposals_written,
    max(
        CASE
            WHEN (stage = 'xfw'::text) THEN proposals_skipped
            ELSE NULL::integer
        END) AS proposals_skipped,
    max(
        CASE
            WHEN (stage = 'xfw'::text) THEN xfw_targets
            ELSE NULL::text[]
        END) AS xfw_targets,
    max(total_ms) AS total_ms,
    max(error_type) AS error_type,
    max(error_detail) AS error_detail,
    bool_or((stage_status = 'error'::text)) AS had_error,
    min(traced_at) AS started_at,
    max(traced_at) AS completed_at
   FROM public.intake_trace_log
  GROUP BY trace_id, tenant_id, upload_id, filename;


--
-- Name: v_posture_confirmation_summary; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_posture_confirmation_summary AS
 SELECT tenant_id,
    standard_id,
    count(*) AS total_controls,
    count(*) FILTER (WHERE (confirmation_status = 'confirmed'::text)) AS confirmed,
    count(*) FILTER (WHERE (confirmation_status = 'draft'::text)) AS draft,
    count(*) FILTER (WHERE (confirmation_status = 'overridden'::text)) AS overridden,
    round(((100.0 * (count(*) FILTER (WHERE (confirmation_status = ANY (ARRAY['confirmed'::text, 'overridden'::text]))))::numeric) / (NULLIF(count(*), 0))::numeric), 1) AS pct_confirmed,
    min(confirmed_at) AS first_confirmed_at,
    max(confirmed_at) AS last_confirmed_at
   FROM public.posture_controls
  WHERE (is_active = true)
  GROUP BY tenant_id, standard_id;


--
-- Name: v_posture_review_queue; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_posture_review_queue AS
 SELECT id,
    tenant_id,
    control_ref,
    standard_id,
    finding,
    gap_description,
    confirmation_status,
    source,
    confidence,
    system_finding,
    system_gap,
    system_proposed_at,
    (EXTRACT(epoch FROM (now() - COALESCE(system_proposed_at, now()))) / (3600)::numeric) AS hours_in_draft,
    (EXISTS ( SELECT 1
           FROM public.confirmation_log cl
          WHERE ((cl.posture_control_id = pc.id) AND (cl.action = 'overridden'::text)))) AS previously_overridden
   FROM public.posture_controls pc
  WHERE ((confirmation_status = 'draft'::text) AND (is_active = true))
  ORDER BY
        CASE finding
            WHEN 'NC'::text THEN 1
            WHEN 'OFI'::text THEN 2
            WHEN 'Comply'::text THEN 3
            WHEN 'N/A'::text THEN 4
            ELSE 5
        END, control_ref;


--
-- Name: v_posture_summary; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_posture_summary AS
 SELECT tenant_id,
    count(*) AS total_controls,
    count(*) FILTER (WHERE (finding = 'NC'::text)) AS nc_count,
    count(*) FILTER (WHERE (finding = 'OFI'::text)) AS ofi_count,
    count(*) FILTER (WHERE (finding = 'Comply'::text)) AS comply_count,
    count(*) FILTER (WHERE (finding = 'Not assessed'::text)) AS unassessed_count,
    count(*) FILTER (WHERE (finding = 'N/A'::text)) AS na_count,
    round((((count(*) FILTER (WHERE (finding = 'Comply'::text)))::numeric / (NULLIF(count(*) FILTER (WHERE (finding <> 'Not assessed'::text)), 0))::numeric) * (100)::numeric), 1) AS comply_percentage,
    max(last_updated) AS last_updated
   FROM public.posture_controls
  GROUP BY tenant_id;


--
-- Name: v_registration_status; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_registration_status AS
 SELECT t.id AS tenant_id,
    t.name AS tenant_name,
    t.onboarding_status,
    count(DISTINCT u.id) AS user_count,
    count(DISTINCT ts.id) AS standards_count,
    count(DISTINCT pc.id) AS posture_controls,
    count(DISTINCT du.id) AS documents_uploaded,
        CASE
            WHEN ((count(DISTINCT u.id) > 0) AND (count(DISTINCT ts.id) > 0) AND (count(DISTINCT pc.id) > 0)) THEN 100
            WHEN (count(DISTINCT ts.id) > 0) THEN 50
            ELSE 20
        END AS onboarding_score
   FROM ((((public.tenants t
     LEFT JOIN public.users u ON ((u.tenant_id = t.id)))
     LEFT JOIN public.tenant_standards ts ON ((ts.tenant_id = t.id)))
     LEFT JOIN public.posture_controls pc ON ((pc.tenant_id = t.id)))
     LEFT JOIN public.document_uploads du ON ((du.tenant_id = t.id)))
  GROUP BY t.id, t.name, t.onboarding_status;


--
-- Name: v_retention_warnings; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_retention_warnings AS
 SELECT 'posture_history'::text AS source_table,
    (posture_history.tenant_id)::text AS tenant_id,
    (posture_history.id)::text AS record_id,
    posture_history.created_at AS record_date,
    posture_history.expires_at,
    (EXTRACT(day FROM (posture_history.expires_at - now())))::integer AS days_remaining
   FROM public.posture_history
  WHERE ((posture_history.expires_at >= now()) AND (posture_history.expires_at <= (now() + '90 days'::interval)))
UNION ALL
 SELECT 'incidents'::text AS source_table,
    (incidents.tenant_id)::text AS tenant_id,
    (incidents.id)::text AS record_id,
    incidents.reported_at AS record_date,
    incidents.expires_at,
    (EXTRACT(day FROM (incidents.expires_at - now())))::integer AS days_remaining
   FROM public.incidents
  WHERE ((incidents.expires_at IS NOT NULL) AND ((incidents.expires_at >= now()) AND (incidents.expires_at <= (now() + '180 days'::interval))))
  ORDER BY 6;


--
-- Name: v_slow_requests; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_slow_requests AS
 SELECT request_id,
    tenant_id,
    taxonomy_type,
    strategy,
    total_ms,
    neo4j_ms,
    vector_ms,
    postgres_ms,
    (nodes_primary + nodes_secondary) AS total_nodes,
    vector_hits,
    traced_at
   FROM public.request_trace_log
  WHERE ((total_ms > 15000) AND (traced_at >= (now() - '7 days'::interval)))
  ORDER BY total_ms DESC;


--
-- Name: v_source_usage; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_source_usage AS
 SELECT tenant_id,
    strategy,
    count(*) AS request_count,
    round(avg(total_ms)) AS avg_latency_ms,
    round(avg((nodes_primary + nodes_secondary))) AS avg_nodes_returned,
    round(avg(vector_hits)) AS avg_vector_hits
   FROM public.request_trace_log
  WHERE (traced_at >= (now() - '30 days'::interval))
  GROUP BY tenant_id, strategy
  ORDER BY tenant_id, (count(*)) DESC;


--
-- Name: v_tenant_request_stats; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_tenant_request_stats AS
 SELECT tenant_id,
    taxonomy_type,
    count(*) AS total_requests,
    round(avg(total_ms)) AS avg_latency_ms,
    round(percentile_cont((0.95)::double precision) WITHIN GROUP (ORDER BY ((total_ms)::double precision))) AS p95_latency_ms,
    max(total_ms) AS max_latency_ms,
    count(*) FILTER (WHERE (error_type IS NOT NULL)) AS error_count,
    count(*) FILTER (WHERE (short_circuit = true)) AS short_circuit_count,
    min(traced_at) AS first_request,
    max(traced_at) AS last_request
   FROM public.request_trace_log
  WHERE (traced_at >= (now() - '30 days'::interval))
  GROUP BY tenant_id, taxonomy_type
  ORDER BY tenant_id, (count(*)) DESC;


--
-- Name: vendors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vendors (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name text NOT NULL,
    service_provided text,
    vendor_category text,
    data_subject_categories text[],
    data_shared text,
    data_location text,
    dpa_signed boolean,
    dpa_date date,
    dpa_reference text,
    risk_level text,
    security_controls text,
    compliance_certs text[],
    last_review_date date,
    next_review_date date,
    notes text,
    is_processor boolean DEFAULT false NOT NULL,
    workbook_imported boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    platform_ref text,
    is_active boolean DEFAULT true NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by uuid,
    deletion_reason text,
    retention_class text DEFAULT 'operational'::text NOT NULL,
    purge_after timestamp with time zone,
    CONSTRAINT vendors_risk_level_check CHECK (((risk_level = ANY (ARRAY['High'::text, 'Medium'::text, 'Low'::text])) OR (risk_level IS NULL)))
);


--
-- Name: workbook_intake_proposal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workbook_intake_proposal (
    id bigint NOT NULL,
    tenant_id uuid NOT NULL,
    discovery_run_id uuid NOT NULL,
    workbook_uri text NOT NULL,
    sheet_name text NOT NULL,
    mapping_id text NOT NULL,
    mapping_path text,
    confidence numeric(5,3) NOT NULL,
    header_row integer,
    row_count integer DEFAULT 0 NOT NULL,
    proposal jsonb NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    decided_at timestamp with time zone,
    decided_by text,
    decision_note text,
    superseded_at timestamp with time zone,
    superseded_by_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    client_document_id uuid,
    CONSTRAINT workbook_intake_proposal_confidence_range CHECK (((confidence >= (0)::numeric) AND (confidence <= (1)::numeric))),
    CONSTRAINT workbook_intake_proposal_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'superseded'::text]))),
    CONSTRAINT workbook_intake_proposal_superseded_consistency CHECK (((status = 'superseded'::text) = (superseded_at IS NOT NULL)))
);


--
-- Name: workbook_intake_proposal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.workbook_intake_proposal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: workbook_intake_proposal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.workbook_intake_proposal_id_seq OWNED BY public.workbook_intake_proposal.id;


--
-- Name: audit_log_2025; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ATTACH PARTITION public.audit_log_2025 FOR VALUES FROM ('2024-12-31 23:00:00+00') TO ('2025-12-31 23:00:00+00');


--
-- Name: audit_log_2026; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ATTACH PARTITION public.audit_log_2026 FOR VALUES FROM ('2025-12-31 23:00:00+00') TO ('2026-12-31 23:00:00+00');


--
-- Name: audit_log_2027; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ATTACH PARTITION public.audit_log_2027 FOR VALUES FROM ('2026-12-31 23:00:00+00') TO ('2027-12-31 23:00:00+00');


--
-- Name: audit_log_2028; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ATTACH PARTITION public.audit_log_2028 FOR VALUES FROM ('2027-12-31 23:00:00+00') TO ('2028-12-31 23:00:00+00');


--
-- Name: posture_history_2025; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history ATTACH PARTITION public.posture_history_2025 FOR VALUES FROM ('2024-12-31 23:00:00+00') TO ('2025-12-31 23:00:00+00');


--
-- Name: posture_history_2026; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history ATTACH PARTITION public.posture_history_2026 FOR VALUES FROM ('2025-12-31 23:00:00+00') TO ('2026-12-31 23:00:00+00');


--
-- Name: posture_history_2027; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history ATTACH PARTITION public.posture_history_2027 FOR VALUES FROM ('2026-12-31 23:00:00+00') TO ('2027-12-31 23:00:00+00');


--
-- Name: posture_history_2028; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history ATTACH PARTITION public.posture_history_2028 FOR VALUES FROM ('2027-12-31 23:00:00+00') TO ('2028-12-31 23:00:00+00');


--
-- Name: posture_assertions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_assertions ALTER COLUMN id SET DEFAULT nextval('public.posture_assertions_id_seq'::regclass);


--
-- Name: posture_must_bridge_coverage id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_bridge_coverage ALTER COLUMN id SET DEFAULT nextval('public.posture_must_bridge_coverage_id_seq'::regclass);


--
-- Name: posture_must_verdicts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_verdicts ALTER COLUMN id SET DEFAULT nextval('public.posture_must_verdicts_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: workbook_intake_proposal id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workbook_intake_proposal ALTER COLUMN id SET DEFAULT nextval('public.workbook_intake_proposal_id_seq'::regclass);


--
-- Name: ai_call_log ai_call_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_log
    ADD CONSTRAINT ai_call_log_pkey PRIMARY KEY (id);


--
-- Name: api_keys api_keys_key_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_key_hash_key UNIQUE (key_hash);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: api_rate_limit_bucket api_rate_limit_bucket_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_rate_limit_bucket
    ADD CONSTRAINT api_rate_limit_bucket_pkey PRIMARY KEY (key_id);


--
-- Name: applicable_standards applicable_standards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applicable_standards
    ADD CONSTRAINT applicable_standards_pkey PRIMARY KEY (tenant_id, standard_id);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: assets assets_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_platform_ref_key UNIQUE (platform_ref);


--
-- Name: assets assets_tenant_id_external_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_tenant_id_external_ref_key UNIQUE (tenant_id, external_ref);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id, created_at);


--
-- Name: audit_log_2025 audit_log_2025_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log_2025
    ADD CONSTRAINT audit_log_2025_pkey PRIMARY KEY (id, created_at);


--
-- Name: audit_log_2026 audit_log_2026_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log_2026
    ADD CONSTRAINT audit_log_2026_pkey PRIMARY KEY (id, created_at);


--
-- Name: audit_log_2027 audit_log_2027_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log_2027
    ADD CONSTRAINT audit_log_2027_pkey PRIMARY KEY (id, created_at);


--
-- Name: audit_log_2028 audit_log_2028_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log_2028
    ADD CONSTRAINT audit_log_2028_pkey PRIMARY KEY (id, created_at);


--
-- Name: cascade_suppression_log cascade_suppression_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_pkey PRIMARY KEY (id);


--
-- Name: chat_casefile_log chat_casefile_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_casefile_log
    ADD CONSTRAINT chat_casefile_log_pkey PRIMARY KEY (id);


--
-- Name: chat_consensus_log chat_consensus_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_consensus_log
    ADD CONSTRAINT chat_consensus_log_pkey PRIMARY KEY (id);


--
-- Name: cite_attestation_prompt cite_attestation_prompt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_pkey PRIMARY KEY (id);


--
-- Name: client_documents client_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_pkey PRIMARY KEY (id);


--
-- Name: client_documents client_documents_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_platform_ref_key UNIQUE (platform_ref);


--
-- Name: client_fact_change_log client_fact_change_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_fact_change_log
    ADD CONSTRAINT client_fact_change_log_pkey PRIMARY KEY (id);


--
-- Name: client_facts client_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_facts
    ADD CONSTRAINT client_facts_pkey PRIMARY KEY (id);


--
-- Name: client_facts client_facts_tenant_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_facts
    ADD CONSTRAINT client_facts_tenant_id_key UNIQUE (tenant_id);


--
-- Name: confirmation_log confirmation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confirmation_log
    ADD CONSTRAINT confirmation_log_pkey PRIMARY KEY (id);


--
-- Name: control_documents control_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_pkey PRIMARY KEY (id);


--
-- Name: control_documents control_documents_tenant_id_control_id_document_id_relation_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_tenant_id_control_id_document_id_relation_key UNIQUE (tenant_id, control_id, document_id, relationship);


--
-- Name: deletion_log deletion_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deletion_log
    ADD CONSTRAINT deletion_log_pkey PRIMARY KEY (id);


--
-- Name: document_findings document_findings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_pkey PRIMARY KEY (id);


--
-- Name: document_findings document_findings_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_platform_ref_key UNIQUE (platform_ref);


--
-- Name: document_sections document_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sections
    ADD CONSTRAINT document_sections_pkey PRIMARY KEY (id);


--
-- Name: document_text document_text_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_text
    ADD CONSTRAINT document_text_pkey PRIMARY KEY (upload_id);


--
-- Name: document_uploads document_uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_uploads
    ADD CONSTRAINT document_uploads_pkey PRIMARY KEY (id);


--
-- Name: enricher_cache enricher_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enricher_cache
    ADD CONSTRAINT enricher_cache_pkey PRIMARY KEY (sha256);


--
-- Name: expected_followup_event expected_followup_event_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expected_followup_event
    ADD CONSTRAINT expected_followup_event_pkey PRIMARY KEY (id);


--
-- Name: external_evidence_source external_evidence_source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_evidence_source
    ADD CONSTRAINT external_evidence_source_pkey PRIMARY KEY (id);


--
-- Name: external_evidence_verification_log external_evidence_verification_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_evidence_verification_log
    ADD CONSTRAINT external_evidence_verification_log_pkey PRIMARY KEY (id);


--
-- Name: fact_recompute_log fact_recompute_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fact_recompute_log
    ADD CONSTRAINT fact_recompute_log_pkey PRIMARY KEY (id);


--
-- Name: fact_source_config fact_source_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fact_source_config
    ADD CONSTRAINT fact_source_config_pkey PRIMARY KEY (id);


--
-- Name: incident_classifications incident_classifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_classifications
    ADD CONSTRAINT incident_classifications_pkey PRIMARY KEY (incident_id, standard_id, dimension, value);


--
-- Name: incident_documents incident_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_pkey PRIMARY KEY (incident_id, document_id, standard_id);


--
-- Name: incident_obligations incident_obligations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_obligations
    ADD CONSTRAINT incident_obligations_pkey PRIMARY KEY (incident_id, control_ref, standard_id);


--
-- Name: incident_timeline incident_timeline_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_timeline
    ADD CONSTRAINT incident_timeline_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_platform_ref_key UNIQUE (platform_ref);


--
-- Name: intake_consensus_log intake_consensus_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_consensus_log
    ADD CONSTRAINT intake_consensus_log_pkey PRIMARY KEY (id);


--
-- Name: intake_trace_log intake_trace_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_trace_log
    ADD CONSTRAINT intake_trace_log_pkey PRIMARY KEY (id);


--
-- Name: isms_audits isms_audits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_pkey PRIMARY KEY (id);


--
-- Name: isms_audits isms_audits_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_platform_ref_key UNIQUE (platform_ref);


--
-- Name: isms_audits isms_audits_tenant_id_external_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_tenant_id_external_ref_key UNIQUE (tenant_id, external_ref);


--
-- Name: notification_delivery_attempt notification_delivery_attempt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification_delivery_attempt
    ADD CONSTRAINT notification_delivery_attempt_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: posture_assertions posture_assertions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_assertions
    ADD CONSTRAINT posture_assertions_pkey PRIMARY KEY (id);


--
-- Name: posture_controls posture_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_pkey PRIMARY KEY (id);


--
-- Name: posture_controls posture_controls_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_platform_ref_key UNIQUE (platform_ref);


--
-- Name: posture_history posture_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history
    ADD CONSTRAINT posture_history_pkey PRIMARY KEY (id, created_at);


--
-- Name: posture_history_2025 posture_history_2025_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history_2025
    ADD CONSTRAINT posture_history_2025_pkey PRIMARY KEY (id, created_at);


--
-- Name: posture_history_2026 posture_history_2026_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history_2026
    ADD CONSTRAINT posture_history_2026_pkey PRIMARY KEY (id, created_at);


--
-- Name: posture_history_2027 posture_history_2027_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history_2027
    ADD CONSTRAINT posture_history_2027_pkey PRIMARY KEY (id, created_at);


--
-- Name: posture_history_2028 posture_history_2028_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_history_2028
    ADD CONSTRAINT posture_history_2028_pkey PRIMARY KEY (id, created_at);


--
-- Name: posture_must_bridge_coverage posture_must_bridge_coverage_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_bridge_coverage
    ADD CONSTRAINT posture_must_bridge_coverage_pkey PRIMARY KEY (id);


--
-- Name: posture_must_verdicts posture_must_verdicts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_verdicts
    ADD CONSTRAINT posture_must_verdicts_pkey PRIMARY KEY (id);


--
-- Name: posture_pending posture_pending_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_pending
    ADD CONSTRAINT posture_pending_pkey PRIMARY KEY (id);


--
-- Name: posture_status_log posture_status_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_status_log
    ADD CONSTRAINT posture_status_log_pkey PRIMARY KEY (id);


--
-- Name: ref_prefixes ref_prefixes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ref_prefixes
    ADD CONSTRAINT ref_prefixes_pkey PRIMARY KEY (prefix);


--
-- Name: ref_sequences ref_sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ref_sequences
    ADD CONSTRAINT ref_sequences_pkey PRIMARY KEY (tenant_id, prefix);


--
-- Name: remediation_evidence remediation_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_pkey PRIMARY KEY (id);


--
-- Name: remediation_plans remediation_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_pkey PRIMARY KEY (id);


--
-- Name: remediation_tasks remediation_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT remediation_tasks_pkey PRIMARY KEY (id);


--
-- Name: request_trace_log request_trace_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.request_trace_log
    ADD CONSTRAINT request_trace_log_pkey PRIMARY KEY (id);


--
-- Name: retention_policies retention_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.retention_policies
    ADD CONSTRAINT retention_policies_pkey PRIMARY KEY (id);


--
-- Name: risks risks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_pkey PRIMARY KEY (id);


--
-- Name: risks risks_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_platform_ref_key UNIQUE (platform_ref);


--
-- Name: risks risks_tenant_id_external_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_tenant_id_external_ref_key UNIQUE (tenant_id, external_ref);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: standard_relationships standard_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_relationships
    ADD CONSTRAINT standard_relationships_pkey PRIMARY KEY (id);


--
-- Name: standard_relationships standard_relationships_source_id_target_id_relationship_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_relationships
    ADD CONSTRAINT standard_relationships_source_id_target_id_relationship_key UNIQUE (source_id, target_id, relationship);


--
-- Name: standards standards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standards
    ADD CONSTRAINT standards_pkey PRIMARY KEY (id);


--
-- Name: sweep_log sweep_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sweep_log
    ADD CONSTRAINT sweep_log_pkey PRIMARY KEY (id);


--
-- Name: tabular_evidence_rows tabular_evidence_rows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabular_evidence_rows
    ADD CONSTRAINT tabular_evidence_rows_pkey PRIMARY KEY (id);


--
-- Name: tabular_evidence_rows tabular_evidence_rows_unique_per_doc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabular_evidence_rows
    ADD CONSTRAINT tabular_evidence_rows_unique_per_doc UNIQUE (document_id, leaf_id, row_index);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (leaf_id);


--
-- Name: tenant_cascade_override tenant_cascade_override_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_cascade_override
    ADD CONSTRAINT tenant_cascade_override_pkey PRIMARY KEY (id);


--
-- Name: tenant_evidence_gaps tenant_evidence_gaps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_evidence_gaps
    ADD CONSTRAINT tenant_evidence_gaps_pkey PRIMARY KEY (id);


--
-- Name: tenant_evidence_gaps tenant_evidence_gaps_tenant_id_control_id_leaf_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_evidence_gaps
    ADD CONSTRAINT tenant_evidence_gaps_tenant_id_control_id_leaf_id_key UNIQUE (tenant_id, control_id, leaf_id);


--
-- Name: tenant_external_system tenant_external_system_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_external_system
    ADD CONSTRAINT tenant_external_system_pkey PRIMARY KEY (id);


--
-- Name: tenant_must_overrides tenant_must_overrides_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_must_overrides
    ADD CONSTRAINT tenant_must_overrides_pkey PRIMARY KEY (id);


--
-- Name: tenant_must_overrides tenant_must_overrides_tenant_id_must_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_must_overrides
    ADD CONSTRAINT tenant_must_overrides_tenant_id_must_id_key UNIQUE (tenant_id, must_id);


--
-- Name: tenant_notification_channel tenant_notification_channel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_notification_channel
    ADD CONSTRAINT tenant_notification_channel_pkey PRIMARY KEY (id);


--
-- Name: tenant_notification tenant_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_notification
    ADD CONSTRAINT tenant_notification_pkey PRIMARY KEY (id);


--
-- Name: tenant_profile tenant_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_profile
    ADD CONSTRAINT tenant_profile_pkey PRIMARY KEY (id);


--
-- Name: tenant_profile tenant_profile_unique_per_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_profile
    ADD CONSTRAINT tenant_profile_unique_per_tenant UNIQUE (tenant_id, profile_key);


--
-- Name: tenant_source_registry tenant_source_registry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_source_registry
    ADD CONSTRAINT tenant_source_registry_pkey PRIMARY KEY (id);


--
-- Name: tenant_source_registry tenant_source_registry_tenant_id_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_source_registry
    ADD CONSTRAINT tenant_source_registry_tenant_id_source_id_key UNIQUE (tenant_id, source_id);


--
-- Name: tenant_standards tenant_standards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_standards
    ADD CONSTRAINT tenant_standards_pkey PRIMARY KEY (id);


--
-- Name: tenant_standards tenant_standards_tenant_id_standard_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_standards
    ADD CONSTRAINT tenant_standards_tenant_id_standard_id_key UNIQUE (tenant_id, standard_id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_slug_key UNIQUE (slug);


--
-- Name: topic_leaves topic_leaves_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_leaves
    ADD CONSTRAINT topic_leaves_pkey PRIMARY KEY (topic_slug, leaf_id);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (slug);


--
-- Name: triggered_implication triggered_implication_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.triggered_implication
    ADD CONSTRAINT triggered_implication_pkey PRIMARY KEY (id);


--
-- Name: posture_must_bridge_coverage uq_pmv_bridge_coverage; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_bridge_coverage
    ADD CONSTRAINT uq_pmv_bridge_coverage UNIQUE (tenant_id, target_must_id, target_control_ref, source_must_id, edge_type);


--
-- Name: posture_must_verdicts uq_pmv_tenant_must; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_must_verdicts
    ADD CONSTRAINT uq_pmv_tenant_must UNIQUE (tenant_id, must_id, control_ref);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_platform_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_platform_ref_key UNIQUE (platform_ref);


--
-- Name: vendors vendors_tenant_id_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_tenant_id_name_key UNIQUE (tenant_id, name);


--
-- Name: workbook_intake_proposal workbook_intake_proposal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workbook_intake_proposal
    ADD CONSTRAINT workbook_intake_proposal_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_record; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_record ON ONLY public.audit_log USING btree (table_name, record_id, created_at DESC);


--
-- Name: audit_log_2025_table_name_record_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2025_table_name_record_id_created_at_idx ON public.audit_log_2025 USING btree (table_name, record_id, created_at DESC);


--
-- Name: idx_audit_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_tenant ON ONLY public.audit_log USING btree (tenant_id, created_at DESC);


--
-- Name: audit_log_2025_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2025_tenant_id_created_at_idx ON public.audit_log_2025 USING btree (tenant_id, created_at DESC);


--
-- Name: idx_audit_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_user ON ONLY public.audit_log USING btree (user_id, created_at DESC);


--
-- Name: audit_log_2025_user_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2025_user_id_created_at_idx ON public.audit_log_2025 USING btree (user_id, created_at DESC);


--
-- Name: audit_log_2026_table_name_record_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2026_table_name_record_id_created_at_idx ON public.audit_log_2026 USING btree (table_name, record_id, created_at DESC);


--
-- Name: audit_log_2026_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2026_tenant_id_created_at_idx ON public.audit_log_2026 USING btree (tenant_id, created_at DESC);


--
-- Name: audit_log_2026_user_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2026_user_id_created_at_idx ON public.audit_log_2026 USING btree (user_id, created_at DESC);


--
-- Name: audit_log_2027_table_name_record_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2027_table_name_record_id_created_at_idx ON public.audit_log_2027 USING btree (table_name, record_id, created_at DESC);


--
-- Name: audit_log_2027_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2027_tenant_id_created_at_idx ON public.audit_log_2027 USING btree (tenant_id, created_at DESC);


--
-- Name: audit_log_2027_user_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2027_user_id_created_at_idx ON public.audit_log_2027 USING btree (user_id, created_at DESC);


--
-- Name: audit_log_2028_table_name_record_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2028_table_name_record_id_created_at_idx ON public.audit_log_2028 USING btree (table_name, record_id, created_at DESC);


--
-- Name: audit_log_2028_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2028_tenant_id_created_at_idx ON public.audit_log_2028 USING btree (tenant_id, created_at DESC);


--
-- Name: audit_log_2028_user_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2028_user_id_created_at_idx ON public.audit_log_2028 USING btree (user_id, created_at DESC);


--
-- Name: cite_attestation_prompt_unique_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX cite_attestation_prompt_unique_active ON public.cite_attestation_prompt USING btree (tenant_id, cite_id, candidate_document_id) WHERE (status = 'pending'::text);


--
-- Name: external_evidence_source_unique_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX external_evidence_source_unique_active ON public.external_evidence_source USING btree (tenant_id, must_id, system_id) WHERE (is_active = true);


--
-- Name: idx_ai_call_log_errors; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_call_log_errors ON public.ai_call_log USING btree (tenant_id, called_at DESC) WHERE (error_type IS NOT NULL);


--
-- Name: idx_ai_call_log_purpose_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_call_log_purpose_time ON public.ai_call_log USING btree (purpose, called_at DESC);


--
-- Name: idx_ai_call_log_session; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_call_log_session ON public.ai_call_log USING btree (session_id) WHERE (session_id IS NOT NULL);


--
-- Name: idx_ai_call_log_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_call_log_tenant_time ON public.ai_call_log USING btree (tenant_id, called_at DESC);


--
-- Name: idx_ai_call_log_upload; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_call_log_upload ON public.ai_call_log USING btree (upload_id) WHERE (upload_id IS NOT NULL);


--
-- Name: idx_api_keys_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_api_keys_hash ON public.api_keys USING btree (key_hash) WHERE (is_active = true);


--
-- Name: idx_api_keys_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_api_keys_tenant ON public.api_keys USING btree (tenant_id) WHERE (is_active = true);


--
-- Name: idx_assets_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_assets_active ON public.assets USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_assets_pii; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_assets_pii ON public.assets USING btree (tenant_id, contains_pii) WHERE (contains_pii = true);


--
-- Name: idx_assets_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_assets_tenant ON public.assets USING btree (tenant_id);


--
-- Name: idx_cascade_suppression_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cascade_suppression_source ON public.cascade_suppression_log USING btree (source_verification_id);


--
-- Name: idx_cascade_suppression_target_req; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cascade_suppression_target_req ON public.cascade_suppression_log USING btree (tenant_id, target_requirement_id, fired_at DESC) WHERE (suppression_kind = 'blocks_when'::text);


--
-- Name: idx_cascade_suppression_tenant_fired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cascade_suppression_tenant_fired ON public.cascade_suppression_log USING btree (tenant_id, fired_at DESC);


--
-- Name: idx_ccfl_claim_events; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccfl_claim_events ON public.chat_casefile_log USING btree (tenant_id, created_at DESC) WHERE (claim_events_count > 0);


--
-- Name: idx_ccfl_enabled; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccfl_enabled ON public.chat_casefile_log USING btree (casefile_enabled, created_at DESC);


--
-- Name: idx_ccfl_repaired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccfl_repaired ON public.chat_casefile_log USING btree (tenant_id, created_at DESC) WHERE (repair_events_count > 0);


--
-- Name: idx_ccfl_session; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccfl_session ON public.chat_casefile_log USING btree (session_id, created_at DESC) WHERE (session_id IS NOT NULL);


--
-- Name: idx_ccfl_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccfl_tenant_time ON public.chat_casefile_log USING btree (tenant_id, created_at DESC);


--
-- Name: idx_ccl_fallback; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccl_fallback ON public.chat_consensus_log USING btree (tenant_id, created_at DESC) WHERE (llm_fallback_used = true);


--
-- Name: idx_ccl_session; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccl_session ON public.chat_consensus_log USING btree (session_id, created_at DESC) WHERE (session_id IS NOT NULL);


--
-- Name: idx_ccl_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccl_tenant_time ON public.chat_consensus_log USING btree (tenant_id, created_at DESC);


--
-- Name: idx_ccl_verdict; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ccl_verdict ON public.chat_consensus_log USING btree (verdict, created_at DESC);


--
-- Name: idx_cite_attestation_prompt_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cite_attestation_prompt_expires ON public.cite_attestation_prompt USING btree (expires_at) WHERE (status = 'pending'::text);


--
-- Name: idx_cite_attestation_prompt_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cite_attestation_prompt_pending ON public.cite_attestation_prompt USING btree (tenant_id, created_at DESC) WHERE (status = 'pending'::text);


--
-- Name: idx_cite_attestation_prompt_pending_confidence; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cite_attestation_prompt_pending_confidence ON public.cite_attestation_prompt USING btree (tenant_id, confidence, created_at DESC) WHERE (status = 'pending'::text);


--
-- Name: idx_client_documents_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_documents_active ON public.client_documents USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_client_fact_change_log_fact; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_fact_change_log_fact ON public.client_fact_change_log USING btree (tenant_id, fact_id, fired_at DESC);


--
-- Name: idx_client_fact_change_log_tenant_fired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_fact_change_log_tenant_fired ON public.client_fact_change_log USING btree (tenant_id, fired_at DESC);


--
-- Name: idx_confirmation_log_batch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_confirmation_log_batch ON public.confirmation_log USING btree (batch_id) WHERE (batch_id IS NOT NULL);


--
-- Name: idx_confirmation_log_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_confirmation_log_control ON public.confirmation_log USING btree (tenant_id, control_ref, performed_at DESC);


--
-- Name: idx_confirmation_log_performer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_confirmation_log_performer ON public.confirmation_log USING btree (performed_by, performed_at DESC);


--
-- Name: idx_confirmation_log_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_confirmation_log_tenant ON public.confirmation_log USING btree (tenant_id, performed_at DESC);


--
-- Name: idx_control_documents_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_control_documents_active ON public.control_documents USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_ctrl_docs_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ctrl_docs_control ON public.control_documents USING btree (control_id);


--
-- Name: idx_ctrl_docs_document; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ctrl_docs_document ON public.control_documents USING btree (document_id);


--
-- Name: idx_ctrl_docs_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ctrl_docs_tenant ON public.control_documents USING btree (tenant_id);


--
-- Name: idx_deletion_log_table_record; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_deletion_log_table_record ON public.deletion_log USING btree (table_name, record_id);


--
-- Name: idx_deletion_log_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_deletion_log_tenant ON public.deletion_log USING btree (tenant_id, executed_at DESC);


--
-- Name: idx_deletion_log_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_deletion_log_type ON public.deletion_log USING btree (deletion_type, executed_at DESC);


--
-- Name: idx_doc_findings_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_findings_control ON public.document_findings USING btree (control_ref);


--
-- Name: idx_doc_findings_pending_xfw; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_findings_pending_xfw ON public.document_findings USING btree (tenant_id, extracted_at DESC) WHERE ((confirmed_by IS NULL) AND (inference_source <> 'extracted'::text));


--
-- Name: idx_doc_findings_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_findings_tenant ON public.document_findings USING btree (tenant_id);


--
-- Name: idx_doc_uploads_dup_of; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_uploads_dup_of ON public.document_uploads USING btree (dup_of_upload_id) WHERE (dup_of_upload_id IS NOT NULL);


--
-- Name: idx_doc_uploads_series; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_uploads_series ON public.document_uploads USING btree (series_id, version_no) WHERE (series_id IS NOT NULL);


--
-- Name: idx_doc_uploads_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_uploads_status ON public.document_uploads USING btree (extraction_status);


--
-- Name: idx_doc_uploads_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_uploads_tenant ON public.document_uploads USING btree (tenant_id);


--
-- Name: idx_doc_uploads_tenant_filename_nodup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_uploads_tenant_filename_nodup ON public.document_uploads USING btree (tenant_id, filename) WHERE (extraction_status <> ALL (ARRAY['duplicate'::text, 'failed'::text]));


--
-- Name: idx_docs_controls; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_docs_controls ON public.client_documents USING gin (control_refs) WHERE is_current;


--
-- Name: idx_docs_evidence_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_docs_evidence_type ON public.client_documents USING btree (tenant_id, evidence_type) WHERE is_current;


--
-- Name: idx_docs_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_docs_tenant ON public.client_documents USING btree (tenant_id, is_current);


--
-- Name: idx_document_findings_evidence_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_evidence_group ON public.document_findings USING btree (tenant_id, evidence_group_id) WHERE (evidence_group_id IS NOT NULL);


--
-- Name: idx_document_findings_grounding_method; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_grounding_method ON public.document_findings USING btree (tenant_id, grounding_method);


--
-- Name: idx_document_findings_precision_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_precision_lookup ON public.document_findings USING btree (tenant_id, standard_id, inference_source, review_status) WHERE ((inference_source = 'fingerprint_match'::text) AND (is_active = true) AND (array_length(corroborating_signals, 1) > 0));


--
-- Name: idx_document_findings_resolved_by_upload; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_resolved_by_upload ON public.document_findings USING btree (tenant_id, resolved_by_upload_id) WHERE (resolved_by_upload_id IS NOT NULL);


--
-- Name: idx_document_findings_review_approved; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_review_approved ON public.document_findings USING btree (tenant_id, control_ref) WHERE ((review_status = 'approved'::text) AND (is_active = true));


--
-- Name: idx_document_findings_review_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_review_pending ON public.document_findings USING btree (tenant_id, control_ref) WHERE ((review_status = 'pending'::text) AND (is_active = true));


--
-- Name: idx_document_findings_workbook_proposal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_findings_workbook_proposal ON public.document_findings USING btree (workbook_proposal_id) WHERE (workbook_proposal_id IS NOT NULL);


--
-- Name: idx_document_text_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_document_text_tenant_time ON public.document_text USING btree (tenant_id, parsed_at DESC);


--
-- Name: idx_documents_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_external_ref ON public.client_documents USING btree (tenant_id, external_ref) WHERE (external_ref IS NOT NULL);


--
-- Name: idx_documents_metadata_only; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_metadata_only ON public.client_documents USING btree (tenant_id, is_metadata_only) WHERE (is_metadata_only = true);


--
-- Name: idx_enricher_cache_cached_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_enricher_cache_cached_at ON public.enricher_cache USING btree (cached_at);


--
-- Name: idx_expected_followup_match_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expected_followup_match_target ON public.expected_followup_event USING btree (tenant_id, expected_event_type) WHERE (status = 'pending'::text);


--
-- Name: idx_expected_followup_pending_expired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expected_followup_pending_expired ON public.expected_followup_event USING btree (tenant_id, expires_at) WHERE (status = 'pending'::text);


--
-- Name: idx_expected_followup_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expected_followup_source ON public.expected_followup_event USING btree (source_verification_id);


--
-- Name: idx_expected_followup_tenant_status_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expected_followup_tenant_status_expires ON public.expected_followup_event USING btree (tenant_id, status, expires_at);


--
-- Name: idx_external_evidence_source_origin_finding; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_source_origin_finding ON public.external_evidence_source USING btree (origin_finding_id) WHERE (origin_finding_id IS NOT NULL);


--
-- Name: idx_external_evidence_source_review_due; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_source_review_due ON public.external_evidence_source USING btree (tenant_id, next_review_due) WHERE (is_active = true);


--
-- Name: idx_external_evidence_source_tenant_leaf; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_source_tenant_leaf ON public.external_evidence_source USING btree (tenant_id, leaf_id) WHERE (is_active = true);


--
-- Name: idx_external_evidence_source_tenant_must; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_source_tenant_must ON public.external_evidence_source USING btree (tenant_id, must_id) WHERE (is_active = true);


--
-- Name: idx_external_evidence_source_url_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_source_url_active ON public.external_evidence_source USING btree (tenant_id, hyperlink_url) WHERE ((is_active = true) AND (hyperlink_url IS NOT NULL));


--
-- Name: idx_external_evidence_verification_log_has_events; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_verification_log_has_events ON public.external_evidence_verification_log USING btree (tenant_id, verified_at DESC) WHERE (structured_events <> '[]'::jsonb);


--
-- Name: idx_external_evidence_verification_log_system; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_verification_log_system ON public.external_evidence_verification_log USING btree (tenant_id, system_id, verified_at DESC);


--
-- Name: idx_external_evidence_verification_log_tenant_leaf; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_evidence_verification_log_tenant_leaf ON public.external_evidence_verification_log USING btree (tenant_id, leaf_id, verified_at DESC);


--
-- Name: idx_fact_recompute_recent_changes; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fact_recompute_recent_changes ON public.fact_recompute_log USING btree (tenant_id, computed_at DESC) WHERE (changed = true);


--
-- Name: idx_fact_recompute_tenant_fact_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fact_recompute_tenant_fact_time ON public.fact_recompute_log USING btree (tenant_id, fact_key, computed_at DESC);


--
-- Name: idx_findings_document; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_findings_document ON public.document_findings USING btree (document_id);


--
-- Name: idx_findings_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_findings_pending ON public.document_findings USING btree (tenant_id) WHERE (confirmed_at IS NULL);


--
-- Name: idx_findings_tenant_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_findings_tenant_control ON public.document_findings USING btree (tenant_id, control_ref, status);


--
-- Name: idx_history_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_history_control ON ONLY public.posture_history USING btree (control_id, created_at DESC);


--
-- Name: idx_history_expiry; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_history_expiry ON ONLY public.posture_history USING btree (expires_at);


--
-- Name: idx_history_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_history_tenant ON ONLY public.posture_history USING btree (tenant_id, created_at DESC);


--
-- Name: idx_incident_classifications_incident; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_classifications_incident ON public.incident_classifications USING btree (incident_id) WHERE (is_active = true);


--
-- Name: idx_incident_classifications_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_classifications_lookup ON public.incident_classifications USING btree (standard_id, dimension, value) WHERE (is_active = true);


--
-- Name: idx_incident_classifications_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_classifications_tenant ON public.incident_classifications USING btree (tenant_id);


--
-- Name: idx_incident_obligations_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_obligations_tenant ON public.incident_obligations USING btree (tenant_id);


--
-- Name: idx_incidents_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incidents_active ON public.incidents USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_incidents_deadline; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incidents_deadline ON public.incidents USING btree (tenant_id, deadline_at) WHERE (status = ANY (ARRAY['open'::text, 'in_progress'::text]));


--
-- Name: idx_incidents_expiry; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incidents_expiry ON public.incidents USING btree (expires_at);


--
-- Name: idx_incidents_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incidents_external_ref ON public.incidents USING btree (tenant_id, external_ref) WHERE (external_ref IS NOT NULL);


--
-- Name: idx_incidents_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incidents_tenant ON public.incidents USING btree (tenant_id, status);


--
-- Name: idx_intake_consensus_log_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_consensus_log_tenant_time ON public.intake_consensus_log USING btree (tenant_id, logged_at DESC);


--
-- Name: idx_intake_consensus_log_upload; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_consensus_log_upload ON public.intake_consensus_log USING btree (upload_id);


--
-- Name: idx_intake_trace_errors; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_errors ON public.intake_trace_log USING btree (tenant_id, error_type, traced_at DESC) WHERE (error_type IS NOT NULL);


--
-- Name: idx_intake_trace_quality; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_quality ON public.intake_trace_log USING btree (tenant_id, traced_at DESC) WHERE ((stage = 'extract'::text) AND ((dropped_hallucinated > 0) OR ((findings_kept IS NOT NULL) AND (findings_kept = 0) AND (candidate_controls IS NOT NULL) AND (candidate_controls > 0)) OR (skipped_as_toc IS NOT NULL) OR ((dropped_questionnaire IS NOT NULL) AND (dropped_questionnaire > 0))));


--
-- Name: idx_intake_trace_slow; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_slow ON public.intake_trace_log USING btree (tenant_id, total_ms DESC) WHERE (total_ms > 10000);


--
-- Name: idx_intake_trace_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_tenant_time ON public.intake_trace_log USING btree (tenant_id, traced_at DESC);


--
-- Name: idx_intake_trace_trace_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_trace_id ON public.intake_trace_log USING btree (trace_id);


--
-- Name: idx_intake_trace_upload; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_intake_trace_upload ON public.intake_trace_log USING btree (upload_id) WHERE (upload_id IS NOT NULL);


--
-- Name: idx_isms_audits_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_isms_audits_active ON public.isms_audits USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_isms_audits_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_isms_audits_date ON public.isms_audits USING btree (tenant_id, audit_date DESC);


--
-- Name: idx_isms_audits_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_isms_audits_tenant ON public.isms_audits USING btree (tenant_id);


--
-- Name: idx_nc_tenant_kind; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nc_tenant_kind ON public.tenant_notification_channel USING btree (tenant_id, channel_kind) WHERE (is_active = true);


--
-- Name: idx_nda_failed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nda_failed ON public.notification_delivery_attempt USING btree (tenant_id, attempted_at DESC) WHERE ((error_type IS NOT NULL) AND (delivered_at IS NULL));


--
-- Name: idx_nda_notification; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nda_notification ON public.notification_delivery_attempt USING btree (notification_id);


--
-- Name: idx_nda_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nda_tenant_time ON public.notification_delivery_attempt USING btree (tenant_id, attempted_at DESC);


--
-- Name: idx_notifications_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notifications_tenant ON public.notifications USING btree (tenant_id, type) WHERE (dismissed_at IS NULL);


--
-- Name: idx_notifications_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notifications_user ON public.notifications USING btree (user_id) WHERE (read_at IS NULL);


--
-- Name: idx_pending_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pending_control ON public.posture_pending USING btree (control_id, status);


--
-- Name: idx_pending_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pending_tenant ON public.posture_pending USING btree (tenant_id, status);


--
-- Name: idx_pmv_bridge_role_cross; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_bridge_role_cross ON public.posture_must_bridge_coverage USING btree (tenant_id, source_role, target_role);


--
-- Name: idx_pmv_bridge_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_bridge_source ON public.posture_must_bridge_coverage USING btree (tenant_id, source_must_id);


--
-- Name: idx_pmv_bridge_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_bridge_target ON public.posture_must_bridge_coverage USING btree (tenant_id, target_must_id);


--
-- Name: idx_pmv_framework_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_framework_role ON public.posture_must_verdicts USING btree (tenant_id, framework_role) WHERE (framework_role IS NOT NULL);


--
-- Name: idx_pmv_tenant_control; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_tenant_control ON public.posture_must_verdicts USING btree (tenant_id, control_ref, standard_id);


--
-- Name: idx_pmv_tenant_satisfied; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pmv_tenant_satisfied ON public.posture_must_verdicts USING btree (tenant_id) WHERE satisfied;


--
-- Name: idx_posture_assertions_history; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_assertions_history ON public.posture_assertions USING btree (tenant_id, control_ref, standard_id, source, set_at DESC);


--
-- Name: idx_posture_assertions_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_assertions_lookup ON public.posture_assertions USING btree (tenant_id, control_ref, standard_id) WHERE (status = ANY (ARRAY['active'::text, 'pending'::text]));


--
-- Name: idx_posture_assertions_pending_queue; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_assertions_pending_queue ON public.posture_assertions USING btree (tenant_id, source) WHERE (status = 'pending'::text);


--
-- Name: idx_posture_controls_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_active ON public.posture_controls USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_posture_controls_confirmed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_confirmed ON public.posture_controls USING btree (tenant_id, confirmation_status) WHERE ((confirmation_status = 'confirmed'::text) AND (is_active = true));


--
-- Name: idx_posture_controls_confirmed_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_confirmed_by ON public.posture_controls USING btree (confirmed_by) WHERE (confirmed_by IS NOT NULL);


--
-- Name: idx_posture_controls_draft; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_draft ON public.posture_controls USING btree (tenant_id, confirmation_status) WHERE ((confirmation_status = 'draft'::text) AND (is_active = true));


--
-- Name: idx_posture_controls_engine_proposed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_engine_proposed ON public.posture_controls USING btree (tenant_id, engine_proposal_status) WHERE ((engine_proposal_status = 'proposed'::text) AND (is_active = true));


--
-- Name: idx_posture_controls_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_controls_source ON public.posture_controls USING btree (tenant_id, source) WHERE (is_active = true);


--
-- Name: idx_posture_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_external_ref ON public.posture_controls USING btree (tenant_id, external_ref) WHERE (external_ref IS NOT NULL);


--
-- Name: idx_posture_finding; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_finding ON public.posture_controls USING btree (tenant_id, finding);


--
-- Name: idx_posture_history_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_history_active ON ONLY public.posture_history USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_posture_remediation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_remediation ON public.posture_controls USING btree (tenant_id, remediation_status) WHERE (remediation_status <> 'closed'::text);


--
-- Name: idx_posture_status_log_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_status_log_lookup ON public.posture_status_log USING btree (tenant_id, control_ref, standard_id, changed_at);


--
-- Name: idx_posture_status_log_upload; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_status_log_upload ON public.posture_status_log USING btree (source_upload_id) WHERE (source_upload_id IS NOT NULL);


--
-- Name: idx_posture_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posture_tenant ON public.posture_controls USING btree (tenant_id);


--
-- Name: idx_remediation_plans_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_remediation_plans_active ON public.remediation_plans USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_remediation_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_remediation_tenant ON public.remediation_plans USING btree (tenant_id, status);


--
-- Name: idx_request_trace_errors; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_request_trace_errors ON public.request_trace_log USING btree (tenant_id, error_type, traced_at DESC) WHERE (error_type IS NOT NULL);


--
-- Name: idx_request_trace_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_request_trace_request_id ON public.request_trace_log USING btree (request_id);


--
-- Name: idx_request_trace_slow; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_request_trace_slow ON public.request_trace_log USING btree (tenant_id, total_ms DESC) WHERE (total_ms > 5000);


--
-- Name: idx_request_trace_taxonomy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_request_trace_taxonomy ON public.request_trace_log USING btree (tenant_id, taxonomy_type, traced_at DESC);


--
-- Name: idx_request_trace_tenant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_request_trace_tenant_time ON public.request_trace_log USING btree (tenant_id, traced_at DESC);


--
-- Name: idx_retention_policies_default; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_retention_policies_default ON public.retention_policies USING btree (retention_class, COALESCE(table_name, ''::text)) WHERE (tenant_id IS NULL);


--
-- Name: idx_risks_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risks_active ON public.risks USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_risks_asset; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risks_asset ON public.risks USING btree (asset_id);


--
-- Name: idx_risks_open; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risks_open ON public.risks USING btree (tenant_id, treatment_status) WHERE (treatment_status <> 'implemented'::text);


--
-- Name: idx_risks_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risks_score ON public.risks USING btree (tenant_id, risk_score DESC);


--
-- Name: idx_risks_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_risks_tenant ON public.risks USING btree (tenant_id);


--
-- Name: idx_sections_doc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sections_doc ON public.document_sections USING btree (document_id);


--
-- Name: idx_standards_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_standards_role ON public.standards USING btree (role);


--
-- Name: idx_standards_subject; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_standards_subject ON public.standards USING gin (subject);


--
-- Name: idx_sweep_log_errors; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sweep_log_errors ON public.sweep_log USING btree (started_at DESC) WHERE (status = 'failed'::text);


--
-- Name: idx_sweep_log_tick; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sweep_log_tick ON public.sweep_log USING btree (tick_id);


--
-- Name: idx_sweep_log_type_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sweep_log_type_time ON public.sweep_log USING btree (work_type, started_at DESC);


--
-- Name: idx_tabular_evidence_doc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tabular_evidence_doc ON public.tabular_evidence_rows USING btree (document_id) WHERE (is_active = true);


--
-- Name: idx_tabular_evidence_tenant_leaf; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tabular_evidence_tenant_leaf ON public.tabular_evidence_rows USING btree (tenant_id, leaf_id) WHERE (is_active = true);


--
-- Name: idx_templates_version; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_templates_version ON public.templates USING btree (template_version);


--
-- Name: idx_tenant_cascade_override_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_cascade_override_lookup ON public.tenant_cascade_override USING btree (tenant_id, event_type) WHERE (is_active = true);


--
-- Name: idx_tenant_evidence_gaps_ack; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_evidence_gaps_ack ON public.tenant_evidence_gaps USING btree (tenant_id, status, acknowledged_at DESC) WHERE (status = 'acknowledged'::text);


--
-- Name: idx_tenant_evidence_gaps_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_evidence_gaps_lookup ON public.tenant_evidence_gaps USING btree (tenant_id, control_id, status);


--
-- Name: idx_tenant_external_system_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_external_system_tenant ON public.tenant_external_system USING btree (tenant_id) WHERE (is_active = true);


--
-- Name: idx_tenant_must_overrides_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_must_overrides_tenant ON public.tenant_must_overrides USING btree (tenant_id);


--
-- Name: idx_tenant_notification_tenant_fired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_notification_tenant_fired ON public.tenant_notification USING btree (tenant_id, fired_at DESC);


--
-- Name: idx_tenant_notification_unread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_notification_unread ON public.tenant_notification USING btree (tenant_id, fired_at DESC) WHERE ((read_at IS NULL) AND (dismissed_at IS NULL));


--
-- Name: idx_tenant_profile_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_profile_tenant ON public.tenant_profile USING btree (tenant_id);


--
-- Name: idx_tenant_source_registry_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_source_registry_source ON public.tenant_source_registry USING btree (source_id, status) WHERE (is_active = true);


--
-- Name: idx_tenant_source_registry_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_source_registry_tenant ON public.tenant_source_registry USING btree (tenant_id, status) WHERE (is_active = true);


--
-- Name: idx_tenant_standards_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_standards_active ON public.tenant_standards USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_tenant_standards_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_standards_status ON public.tenant_standards USING btree (tenant_id, status);


--
-- Name: idx_tenant_standards_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_standards_tenant ON public.tenant_standards USING btree (tenant_id);


--
-- Name: idx_tenants_short_code; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_tenants_short_code ON public.tenants USING btree (short_code) WHERE (short_code IS NOT NULL);


--
-- Name: idx_timeline_incident; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_timeline_incident ON public.incident_timeline USING btree (incident_id, actioned_at DESC);


--
-- Name: idx_topic_leaves_leaf_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_topic_leaves_leaf_id ON public.topic_leaves USING btree (leaf_id);


--
-- Name: idx_topics_display_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_topics_display_order ON public.topics USING btree (display_order);


--
-- Name: idx_triggered_implication_pending_due; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_triggered_implication_pending_due ON public.triggered_implication USING btree (tenant_id, due_date) WHERE ((status = 'pending'::text) AND (due_date IS NOT NULL));


--
-- Name: idx_triggered_implication_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_triggered_implication_source ON public.triggered_implication USING btree (source_verification_id);


--
-- Name: idx_triggered_implication_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_triggered_implication_target ON public.triggered_implication USING btree (tenant_id, target_requirement_id);


--
-- Name: idx_triggered_implication_tenant_status_due; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_triggered_implication_tenant_status_due ON public.triggered_implication USING btree (tenant_id, status, due_date);


--
-- Name: idx_user_roles_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_roles_tenant ON public.user_roles USING btree (tenant_id) WHERE is_active;


--
-- Name: idx_user_roles_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_roles_user ON public.user_roles USING btree (user_id) WHERE is_active;


--
-- Name: idx_users_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_active ON public.users USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_users_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_tenant ON public.users USING btree (tenant_id);


--
-- Name: idx_vendors_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendors_active ON public.vendors USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: idx_vendors_processor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendors_processor ON public.vendors USING btree (tenant_id, is_processor) WHERE (is_processor = true);


--
-- Name: idx_vendors_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendors_tenant ON public.vendors USING btree (tenant_id);


--
-- Name: idx_workbook_intake_proposal_client_doc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workbook_intake_proposal_client_doc ON public.workbook_intake_proposal USING btree (tenant_id, client_document_id);


--
-- Name: idx_workbook_intake_proposal_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workbook_intake_proposal_pending ON public.workbook_intake_proposal USING btree (tenant_id, status, created_at DESC) WHERE (status = 'pending'::text);


--
-- Name: idx_workbook_intake_proposal_run; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workbook_intake_proposal_run ON public.workbook_intake_proposal USING btree (tenant_id, discovery_run_id, created_at);


--
-- Name: idx_workbook_intake_proposal_workbook; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workbook_intake_proposal_workbook ON public.workbook_intake_proposal USING btree (tenant_id, workbook_uri, created_at DESC);


--
-- Name: ix_posture_controls_applicability; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_posture_controls_applicability ON public.posture_controls USING btree (tenant_id, applicability_status) WHERE (applicability_status = 'na'::text);


--
-- Name: posture_history_2025_control_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2025_control_id_created_at_idx ON public.posture_history_2025 USING btree (control_id, created_at DESC);


--
-- Name: posture_history_2025_expires_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2025_expires_at_idx ON public.posture_history_2025 USING btree (expires_at);


--
-- Name: posture_history_2025_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2025_tenant_id_created_at_idx ON public.posture_history_2025 USING btree (tenant_id, created_at DESC);


--
-- Name: posture_history_2025_tenant_id_is_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2025_tenant_id_is_active_idx ON public.posture_history_2025 USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: posture_history_2026_control_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2026_control_id_created_at_idx ON public.posture_history_2026 USING btree (control_id, created_at DESC);


--
-- Name: posture_history_2026_expires_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2026_expires_at_idx ON public.posture_history_2026 USING btree (expires_at);


--
-- Name: posture_history_2026_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2026_tenant_id_created_at_idx ON public.posture_history_2026 USING btree (tenant_id, created_at DESC);


--
-- Name: posture_history_2026_tenant_id_is_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2026_tenant_id_is_active_idx ON public.posture_history_2026 USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: posture_history_2027_control_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2027_control_id_created_at_idx ON public.posture_history_2027 USING btree (control_id, created_at DESC);


--
-- Name: posture_history_2027_expires_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2027_expires_at_idx ON public.posture_history_2027 USING btree (expires_at);


--
-- Name: posture_history_2027_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2027_tenant_id_created_at_idx ON public.posture_history_2027 USING btree (tenant_id, created_at DESC);


--
-- Name: posture_history_2027_tenant_id_is_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2027_tenant_id_is_active_idx ON public.posture_history_2027 USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: posture_history_2028_control_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2028_control_id_created_at_idx ON public.posture_history_2028 USING btree (control_id, created_at DESC);


--
-- Name: posture_history_2028_expires_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2028_expires_at_idx ON public.posture_history_2028 USING btree (expires_at);


--
-- Name: posture_history_2028_tenant_id_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2028_tenant_id_created_at_idx ON public.posture_history_2028 USING btree (tenant_id, created_at DESC);


--
-- Name: posture_history_2028_tenant_id_is_active_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX posture_history_2028_tenant_id_is_active_idx ON public.posture_history_2028 USING btree (tenant_id, is_active) WHERE (is_active = true);


--
-- Name: tenant_cascade_override_active_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX tenant_cascade_override_active_unique ON public.tenant_cascade_override USING btree (tenant_id, override_kind, event_type, COALESCE(target_requirement_id, ''::text)) WHERE (is_active = true);


--
-- Name: tenant_external_system_unique_name_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX tenant_external_system_unique_name_active ON public.tenant_external_system USING btree (tenant_id, system_name) WHERE (is_active = true);


--
-- Name: tenant_notification_active_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX tenant_notification_active_unique ON public.tenant_notification USING btree (tenant_id, kind, COALESCE((related_entity_id)::text, ''::text), COALESCE(related_control_ref, ''::text)) WHERE ((read_at IS NULL) AND (dismissed_at IS NULL));


--
-- Name: uidx_client_documents_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uidx_client_documents_external_ref ON public.client_documents USING btree (tenant_id, external_ref);


--
-- Name: uidx_incidents_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uidx_incidents_external_ref ON public.incidents USING btree (tenant_id, external_ref);


--
-- Name: uidx_posture_controls_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uidx_posture_controls_active ON public.posture_controls USING btree (tenant_id, standard_id, control_ref) WHERE (is_active = true);


--
-- Name: uidx_posture_controls_control_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uidx_posture_controls_control_ref ON public.posture_controls USING btree (tenant_id, standard_id, control_ref) WHERE (control_ref IS NOT NULL);


--
-- Name: uidx_posture_controls_external_ref; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uidx_posture_controls_external_ref ON public.posture_controls USING btree (tenant_id, external_ref);


--
-- Name: uniq_document_text_tenant_markdown_sha256; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uniq_document_text_tenant_markdown_sha256 ON public.document_text USING btree (tenant_id, markdown_sha256);


--
-- Name: uniq_document_uploads_series_version; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uniq_document_uploads_series_version ON public.document_uploads USING btree (series_id, version_no) WHERE (series_id IS NOT NULL);


--
-- Name: uniq_document_uploads_tenant_sha256; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uniq_document_uploads_tenant_sha256 ON public.document_uploads USING btree (tenant_id, sha256) WHERE ((sha256 IS NOT NULL) AND (extraction_status <> ALL (ARRAY['duplicate'::text, 'failed'::text])));


--
-- Name: uq_fact_source_config_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_fact_source_config_key ON public.fact_source_config USING btree (fact_key) WHERE (is_active = true);


--
-- Name: uq_posture_assertions_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_posture_assertions_active ON public.posture_assertions USING btree (tenant_id, control_ref, standard_id, source) WHERE (status = 'active'::text);


--
-- Name: uq_posture_assertions_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_posture_assertions_pending ON public.posture_assertions USING btree (tenant_id, control_ref, standard_id, source) WHERE (status = 'pending'::text);


--
-- Name: uq_workbook_intake_proposal_run_sheet_mapping; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_workbook_intake_proposal_run_sheet_mapping ON public.workbook_intake_proposal USING btree (tenant_id, discovery_run_id, sheet_name, mapping_id);


--
-- Name: audit_log_2025_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.audit_log_pkey ATTACH PARTITION public.audit_log_2025_pkey;


--
-- Name: audit_log_2025_table_name_record_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_record ATTACH PARTITION public.audit_log_2025_table_name_record_id_created_at_idx;


--
-- Name: audit_log_2025_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_tenant ATTACH PARTITION public.audit_log_2025_tenant_id_created_at_idx;


--
-- Name: audit_log_2025_user_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_user ATTACH PARTITION public.audit_log_2025_user_id_created_at_idx;


--
-- Name: audit_log_2026_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.audit_log_pkey ATTACH PARTITION public.audit_log_2026_pkey;


--
-- Name: audit_log_2026_table_name_record_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_record ATTACH PARTITION public.audit_log_2026_table_name_record_id_created_at_idx;


--
-- Name: audit_log_2026_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_tenant ATTACH PARTITION public.audit_log_2026_tenant_id_created_at_idx;


--
-- Name: audit_log_2026_user_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_user ATTACH PARTITION public.audit_log_2026_user_id_created_at_idx;


--
-- Name: audit_log_2027_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.audit_log_pkey ATTACH PARTITION public.audit_log_2027_pkey;


--
-- Name: audit_log_2027_table_name_record_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_record ATTACH PARTITION public.audit_log_2027_table_name_record_id_created_at_idx;


--
-- Name: audit_log_2027_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_tenant ATTACH PARTITION public.audit_log_2027_tenant_id_created_at_idx;


--
-- Name: audit_log_2027_user_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_user ATTACH PARTITION public.audit_log_2027_user_id_created_at_idx;


--
-- Name: audit_log_2028_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.audit_log_pkey ATTACH PARTITION public.audit_log_2028_pkey;


--
-- Name: audit_log_2028_table_name_record_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_record ATTACH PARTITION public.audit_log_2028_table_name_record_id_created_at_idx;


--
-- Name: audit_log_2028_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_tenant ATTACH PARTITION public.audit_log_2028_tenant_id_created_at_idx;


--
-- Name: audit_log_2028_user_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_user ATTACH PARTITION public.audit_log_2028_user_id_created_at_idx;


--
-- Name: posture_history_2025_control_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_control ATTACH PARTITION public.posture_history_2025_control_id_created_at_idx;


--
-- Name: posture_history_2025_expires_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_expiry ATTACH PARTITION public.posture_history_2025_expires_at_idx;


--
-- Name: posture_history_2025_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.posture_history_pkey ATTACH PARTITION public.posture_history_2025_pkey;


--
-- Name: posture_history_2025_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_tenant ATTACH PARTITION public.posture_history_2025_tenant_id_created_at_idx;


--
-- Name: posture_history_2025_tenant_id_is_active_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_posture_history_active ATTACH PARTITION public.posture_history_2025_tenant_id_is_active_idx;


--
-- Name: posture_history_2026_control_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_control ATTACH PARTITION public.posture_history_2026_control_id_created_at_idx;


--
-- Name: posture_history_2026_expires_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_expiry ATTACH PARTITION public.posture_history_2026_expires_at_idx;


--
-- Name: posture_history_2026_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.posture_history_pkey ATTACH PARTITION public.posture_history_2026_pkey;


--
-- Name: posture_history_2026_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_tenant ATTACH PARTITION public.posture_history_2026_tenant_id_created_at_idx;


--
-- Name: posture_history_2026_tenant_id_is_active_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_posture_history_active ATTACH PARTITION public.posture_history_2026_tenant_id_is_active_idx;


--
-- Name: posture_history_2027_control_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_control ATTACH PARTITION public.posture_history_2027_control_id_created_at_idx;


--
-- Name: posture_history_2027_expires_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_expiry ATTACH PARTITION public.posture_history_2027_expires_at_idx;


--
-- Name: posture_history_2027_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.posture_history_pkey ATTACH PARTITION public.posture_history_2027_pkey;


--
-- Name: posture_history_2027_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_tenant ATTACH PARTITION public.posture_history_2027_tenant_id_created_at_idx;


--
-- Name: posture_history_2027_tenant_id_is_active_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_posture_history_active ATTACH PARTITION public.posture_history_2027_tenant_id_is_active_idx;


--
-- Name: posture_history_2028_control_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_control ATTACH PARTITION public.posture_history_2028_control_id_created_at_idx;


--
-- Name: posture_history_2028_expires_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_expiry ATTACH PARTITION public.posture_history_2028_expires_at_idx;


--
-- Name: posture_history_2028_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.posture_history_pkey ATTACH PARTITION public.posture_history_2028_pkey;


--
-- Name: posture_history_2028_tenant_id_created_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_history_tenant ATTACH PARTITION public.posture_history_2028_tenant_id_created_at_idx;


--
-- Name: posture_history_2028_tenant_id_is_active_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_posture_history_active ATTACH PARTITION public.posture_history_2028_tenant_id_is_active_idx;


--
-- Name: confirmation_log trg_block_confirmation_log_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_block_confirmation_log_delete BEFORE DELETE ON public.confirmation_log FOR EACH ROW EXECUTE FUNCTION public.fn_block_confirmation_log_delete();


--
-- Name: request_trace_log trg_block_request_trace_delete; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_block_request_trace_delete BEFORE DELETE ON public.request_trace_log FOR EACH ROW EXECUTE FUNCTION public.fn_block_request_trace_delete();


--
-- Name: applicable_standards trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.applicable_standards FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: assets trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.assets FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: client_documents trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.client_documents FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: client_facts trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.client_facts FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: control_documents trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.control_documents FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: document_findings trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.document_findings FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: document_sections trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.document_sections FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: incident_classifications trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.incident_classifications FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: incident_documents trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.incident_documents FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: incident_obligations trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.incident_obligations FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: incident_timeline trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.incident_timeline FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: incidents trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.incidents FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: isms_audits trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.isms_audits FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: notifications trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.notifications FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: posture_controls trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.posture_controls FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: posture_history trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.posture_history FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: posture_pending trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.posture_pending FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: remediation_evidence trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.remediation_evidence FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: remediation_plans trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.remediation_plans FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: remediation_tasks trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.remediation_tasks FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: risks trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.risks FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: tenant_source_registry trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.tenant_source_registry FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: tenant_standards trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.tenant_standards FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: user_roles trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.user_roles FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: users trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.users FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: vendors trg_compute_purge_after; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_compute_purge_after BEFORE UPDATE OF is_active ON public.vendors FOR EACH ROW EXECUTE FUNCTION public.fn_compute_purge_after();


--
-- Name: client_documents trg_document_status; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_document_status BEFORE UPDATE OF storage_path ON public.client_documents FOR EACH ROW EXECUTE FUNCTION public.fn_update_document_status();


--
-- Name: posture_controls trg_posture_confirmation; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_posture_confirmation BEFORE UPDATE OF confirmation_status ON public.posture_controls FOR EACH ROW EXECUTE FUNCTION public.fn_posture_confirmation_guard();


--
-- Name: posture_controls trg_posture_controls_to_assertion; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_posture_controls_to_assertion AFTER INSERT OR UPDATE ON public.posture_controls FOR EACH ROW EXECUTE FUNCTION public.fn_posture_controls_to_assertion();


--
-- Name: posture_controls trg_posture_write_guard; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_posture_write_guard BEFORE INSERT OR UPDATE ON public.posture_controls FOR EACH ROW EXECUTE FUNCTION public.fn_posture_write_guard();


--
-- Name: workbook_intake_proposal trg_workbook_intake_proposal_touch_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_workbook_intake_proposal_touch_updated_at BEFORE UPDATE ON public.workbook_intake_proposal FOR EACH ROW EXECUTE FUNCTION public.fn_workbook_intake_proposal_touch_updated_at();


--
-- Name: ai_call_log ai_call_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_call_log
    ADD CONSTRAINT ai_call_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: api_keys api_keys_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: api_keys api_keys_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: api_keys api_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: api_rate_limit_bucket api_rate_limit_bucket_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_rate_limit_bucket
    ADD CONSTRAINT api_rate_limit_bucket_key_id_fkey FOREIGN KEY (key_id) REFERENCES public.api_keys(id) ON DELETE CASCADE;


--
-- Name: applicable_standards applicable_standards_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applicable_standards
    ADD CONSTRAINT applicable_standards_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: applicable_standards applicable_standards_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applicable_standards
    ADD CONSTRAINT applicable_standards_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: assets assets_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: assets assets_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_owner_fkey FOREIGN KEY (owner) REFERENCES public.users(id);


--
-- Name: assets assets_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: cascade_suppression_log cascade_suppression_log_source_verification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_source_verification_id_fkey FOREIGN KEY (source_verification_id) REFERENCES public.external_evidence_verification_log(id) ON DELETE CASCADE;


--
-- Name: chat_casefile_log chat_casefile_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_casefile_log
    ADD CONSTRAINT chat_casefile_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: chat_consensus_log chat_consensus_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_consensus_log
    ADD CONSTRAINT chat_consensus_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: cite_attestation_prompt cite_attestation_prompt_candidate_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_candidate_document_id_fkey FOREIGN KEY (candidate_document_id) REFERENCES public.client_documents(id) ON DELETE CASCADE;


--
-- Name: cite_attestation_prompt cite_attestation_prompt_cite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_cite_id_fkey FOREIGN KEY (cite_id) REFERENCES public.external_evidence_source(id) ON DELETE CASCADE;


--
-- Name: cite_attestation_prompt cite_attestation_prompt_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: cite_attestation_prompt cite_attestation_prompt_verification_log_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_verification_log_id_fkey FOREIGN KEY (verification_log_id) REFERENCES public.external_evidence_verification_log(id) ON DELETE SET NULL;


--
-- Name: client_documents client_documents_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: client_documents client_documents_superseded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_superseded_by_fkey FOREIGN KEY (superseded_by) REFERENCES public.client_documents(id);


--
-- Name: client_documents client_documents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: client_documents client_documents_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_documents
    ADD CONSTRAINT client_documents_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: client_fact_change_log client_fact_change_log_source_verification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_fact_change_log
    ADD CONSTRAINT client_fact_change_log_source_verification_id_fkey FOREIGN KEY (source_verification_id) REFERENCES public.external_evidence_verification_log(id) ON DELETE CASCADE;


--
-- Name: client_facts client_facts_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_facts
    ADD CONSTRAINT client_facts_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: client_facts client_facts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_facts
    ADD CONSTRAINT client_facts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: client_facts client_facts_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_facts
    ADD CONSTRAINT client_facts_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: confirmation_log confirmation_log_performed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confirmation_log
    ADD CONSTRAINT confirmation_log_performed_by_fkey FOREIGN KEY (performed_by) REFERENCES public.users(id);


--
-- Name: confirmation_log confirmation_log_posture_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confirmation_log
    ADD CONSTRAINT confirmation_log_posture_control_id_fkey FOREIGN KEY (posture_control_id) REFERENCES public.posture_controls(id);


--
-- Name: confirmation_log confirmation_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confirmation_log
    ADD CONSTRAINT confirmation_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: control_documents control_documents_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.posture_controls(id);


--
-- Name: control_documents control_documents_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: control_documents control_documents_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id);


--
-- Name: control_documents control_documents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.control_documents
    ADD CONSTRAINT control_documents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: deletion_log deletion_log_executed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deletion_log
    ADD CONSTRAINT deletion_log_executed_by_fkey FOREIGN KEY (executed_by) REFERENCES public.users(id);


--
-- Name: deletion_log deletion_log_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deletion_log
    ADD CONSTRAINT deletion_log_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.users(id);


--
-- Name: deletion_log deletion_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deletion_log
    ADD CONSTRAINT deletion_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: document_findings document_findings_confirmed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_confirmed_by_fkey FOREIGN KEY (confirmed_by) REFERENCES public.users(id);


--
-- Name: document_findings document_findings_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: document_findings document_findings_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id);


--
-- Name: document_findings document_findings_resolved_by_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_resolved_by_upload_id_fkey FOREIGN KEY (resolved_by_upload_id) REFERENCES public.document_uploads(id) ON DELETE SET NULL;


--
-- Name: document_findings document_findings_workbook_proposal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_findings
    ADD CONSTRAINT document_findings_workbook_proposal_id_fkey FOREIGN KEY (workbook_proposal_id) REFERENCES public.workbook_intake_proposal(id) ON DELETE SET NULL;


--
-- Name: document_sections document_sections_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sections
    ADD CONSTRAINT document_sections_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: document_sections document_sections_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_sections
    ADD CONSTRAINT document_sections_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id);


--
-- Name: document_text document_text_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_text
    ADD CONSTRAINT document_text_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: document_text document_text_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_text
    ADD CONSTRAINT document_text_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES public.document_uploads(id) ON DELETE CASCADE;


--
-- Name: document_uploads document_uploads_dup_of_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_uploads
    ADD CONSTRAINT document_uploads_dup_of_upload_id_fkey FOREIGN KEY (dup_of_upload_id) REFERENCES public.document_uploads(id) ON DELETE SET NULL;


--
-- Name: document_uploads document_uploads_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_uploads
    ADD CONSTRAINT document_uploads_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: document_uploads document_uploads_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_uploads
    ADD CONSTRAINT document_uploads_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: expected_followup_event expected_followup_event_source_verification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expected_followup_event
    ADD CONSTRAINT expected_followup_event_source_verification_id_fkey FOREIGN KEY (source_verification_id) REFERENCES public.external_evidence_verification_log(id) ON DELETE CASCADE;


--
-- Name: external_evidence_source external_evidence_source_origin_finding_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_evidence_source
    ADD CONSTRAINT external_evidence_source_origin_finding_id_fkey FOREIGN KEY (origin_finding_id) REFERENCES public.document_findings(id) ON DELETE SET NULL;


--
-- Name: external_evidence_source external_evidence_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_evidence_source
    ADD CONSTRAINT external_evidence_source_system_id_fkey FOREIGN KEY (system_id) REFERENCES public.tenant_external_system(id);


--
-- Name: external_evidence_verification_log external_evidence_verification_log_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_evidence_verification_log
    ADD CONSTRAINT external_evidence_verification_log_system_id_fkey FOREIGN KEY (system_id) REFERENCES public.tenant_external_system(id);


--
-- Name: fact_recompute_log fact_recompute_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fact_recompute_log
    ADD CONSTRAINT fact_recompute_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: incident_classifications incident_classifications_classified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_classifications
    ADD CONSTRAINT incident_classifications_classified_by_fkey FOREIGN KEY (classified_by) REFERENCES public.users(id);


--
-- Name: incident_classifications incident_classifications_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_classifications
    ADD CONSTRAINT incident_classifications_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: incident_classifications incident_classifications_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_classifications
    ADD CONSTRAINT incident_classifications_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: incident_classifications incident_classifications_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_classifications
    ADD CONSTRAINT incident_classifications_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: incident_documents incident_documents_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: incident_documents incident_documents_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id);


--
-- Name: incident_documents incident_documents_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: incident_documents incident_documents_linked_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_linked_by_fkey FOREIGN KEY (linked_by) REFERENCES public.users(id);


--
-- Name: incident_documents incident_documents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_documents
    ADD CONSTRAINT incident_documents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: incident_obligations incident_obligations_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_obligations
    ADD CONSTRAINT incident_obligations_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: incident_obligations incident_obligations_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_obligations
    ADD CONSTRAINT incident_obligations_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: incident_obligations incident_obligations_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_obligations
    ADD CONSTRAINT incident_obligations_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: incident_timeline incident_timeline_actioned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_timeline
    ADD CONSTRAINT incident_timeline_actioned_by_fkey FOREIGN KEY (actioned_by) REFERENCES public.users(id);


--
-- Name: incident_timeline incident_timeline_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_timeline
    ADD CONSTRAINT incident_timeline_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: incident_timeline incident_timeline_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_timeline
    ADD CONSTRAINT incident_timeline_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id);


--
-- Name: incidents incidents_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: incidents incidents_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: incidents incidents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: intake_trace_log intake_trace_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_trace_log
    ADD CONSTRAINT intake_trace_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: isms_audits isms_audits_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: isms_audits isms_audits_report_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_report_document_id_fkey FOREIGN KEY (report_document_id) REFERENCES public.client_documents(id);


--
-- Name: isms_audits isms_audits_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.isms_audits
    ADD CONSTRAINT isms_audits_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: notification_delivery_attempt notification_delivery_attempt_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification_delivery_attempt
    ADD CONSTRAINT notification_delivery_attempt_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.tenant_notification_channel(id);


--
-- Name: notifications notifications_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: notifications notifications_target_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_target_role_fkey FOREIGN KEY (target_role) REFERENCES public.roles(name);


--
-- Name: notifications notifications_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: posture_assertions posture_assertions_superseded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_assertions
    ADD CONSTRAINT posture_assertions_superseded_by_id_fkey FOREIGN KEY (superseded_by_id) REFERENCES public.posture_assertions(id) ON DELETE SET NULL;


--
-- Name: posture_assertions posture_assertions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_assertions
    ADD CONSTRAINT posture_assertions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: posture_controls posture_controls_confirmed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_confirmed_by_fkey FOREIGN KEY (confirmed_by) REFERENCES public.users(id);


--
-- Name: posture_controls posture_controls_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: posture_controls posture_controls_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_owner_fkey FOREIGN KEY (owner) REFERENCES public.users(id);


--
-- Name: posture_controls posture_controls_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_controls
    ADD CONSTRAINT posture_controls_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: posture_history posture_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.posture_history
    ADD CONSTRAINT posture_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id);


--
-- Name: posture_history posture_history_confirmed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.posture_history
    ADD CONSTRAINT posture_history_confirmed_by_fkey FOREIGN KEY (confirmed_by) REFERENCES public.users(id);


--
-- Name: posture_history posture_history_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.posture_history
    ADD CONSTRAINT posture_history_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.posture_controls(id);


--
-- Name: posture_history posture_history_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.posture_history
    ADD CONSTRAINT posture_history_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: posture_pending posture_pending_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_pending
    ADD CONSTRAINT posture_pending_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.posture_controls(id);


--
-- Name: posture_pending posture_pending_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_pending
    ADD CONSTRAINT posture_pending_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: posture_pending posture_pending_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_pending
    ADD CONSTRAINT posture_pending_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- Name: posture_pending posture_pending_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_pending
    ADD CONSTRAINT posture_pending_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: posture_status_log posture_status_log_posture_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_status_log
    ADD CONSTRAINT posture_status_log_posture_id_fkey FOREIGN KEY (posture_id) REFERENCES public.posture_controls(id) ON DELETE SET NULL;


--
-- Name: posture_status_log posture_status_log_source_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_status_log
    ADD CONSTRAINT posture_status_log_source_upload_id_fkey FOREIGN KEY (source_upload_id) REFERENCES public.document_uploads(id) ON DELETE SET NULL;


--
-- Name: posture_status_log posture_status_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posture_status_log
    ADD CONSTRAINT posture_status_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: ref_sequences ref_sequences_prefix_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ref_sequences
    ADD CONSTRAINT ref_sequences_prefix_fkey FOREIGN KEY (prefix) REFERENCES public.ref_prefixes(prefix);


--
-- Name: ref_sequences ref_sequences_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ref_sequences
    ADD CONSTRAINT ref_sequences_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: remediation_evidence remediation_evidence_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: remediation_evidence remediation_evidence_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id);


--
-- Name: remediation_evidence remediation_evidence_submitted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_submitted_by_fkey FOREIGN KEY (submitted_by) REFERENCES public.users(id);


--
-- Name: remediation_evidence remediation_evidence_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.remediation_tasks(id);


--
-- Name: remediation_evidence remediation_evidence_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_evidence
    ADD CONSTRAINT remediation_evidence_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: remediation_plans remediation_plans_control_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_control_id_fkey FOREIGN KEY (control_id) REFERENCES public.posture_controls(id);


--
-- Name: remediation_plans remediation_plans_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: remediation_plans remediation_plans_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: remediation_plans remediation_plans_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_owner_fkey FOREIGN KEY (owner) REFERENCES public.users(id);


--
-- Name: remediation_plans remediation_plans_risk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_risk_id_fkey FOREIGN KEY (risk_id) REFERENCES public.risks(id) ON DELETE SET NULL;


--
-- Name: remediation_plans remediation_plans_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_plans
    ADD CONSTRAINT remediation_plans_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: remediation_tasks remediation_tasks_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT remediation_tasks_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: remediation_tasks remediation_tasks_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT remediation_tasks_owner_fkey FOREIGN KEY (owner) REFERENCES public.users(id);


--
-- Name: remediation_tasks remediation_tasks_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT remediation_tasks_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.remediation_plans(id);


--
-- Name: request_trace_log request_trace_log_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.request_trace_log
    ADD CONSTRAINT request_trace_log_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: retention_policies retention_policies_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.retention_policies
    ADD CONSTRAINT retention_policies_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: risks risks_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id) ON DELETE SET NULL;


--
-- Name: risks risks_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: risks risks_risk_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_risk_owner_fkey FOREIGN KEY (risk_owner) REFERENCES public.users(id);


--
-- Name: risks risks_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT risks_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: standard_relationships standard_relationships_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_relationships
    ADD CONSTRAINT standard_relationships_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.standards(id);


--
-- Name: standard_relationships standard_relationships_target_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standard_relationships
    ADD CONSTRAINT standard_relationships_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.standards(id);


--
-- Name: tabular_evidence_rows tabular_evidence_rows_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabular_evidence_rows
    ADD CONSTRAINT tabular_evidence_rows_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.client_documents(id) ON DELETE CASCADE;


--
-- Name: tenant_evidence_gaps tenant_evidence_gaps_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_evidence_gaps
    ADD CONSTRAINT tenant_evidence_gaps_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: tenant_notification_channel tenant_notification_channel_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_notification_channel
    ADD CONSTRAINT tenant_notification_channel_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: tenant_source_registry tenant_source_registry_connected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_source_registry
    ADD CONSTRAINT tenant_source_registry_connected_by_fkey FOREIGN KEY (connected_by) REFERENCES public.users(id);


--
-- Name: tenant_source_registry tenant_source_registry_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_source_registry
    ADD CONSTRAINT tenant_source_registry_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: tenant_source_registry tenant_source_registry_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_source_registry
    ADD CONSTRAINT tenant_source_registry_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: tenant_standards tenant_standards_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_standards
    ADD CONSTRAINT tenant_standards_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: tenant_standards tenant_standards_standard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_standards
    ADD CONSTRAINT tenant_standards_standard_id_fkey FOREIGN KEY (standard_id) REFERENCES public.standards(id);


--
-- Name: tenant_standards tenant_standards_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant_standards
    ADD CONSTRAINT tenant_standards_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: topic_leaves topic_leaves_topic_slug_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.topic_leaves
    ADD CONSTRAINT topic_leaves_topic_slug_fkey FOREIGN KEY (topic_slug) REFERENCES public.topics(slug) ON DELETE CASCADE;


--
-- Name: triggered_implication triggered_implication_source_verification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.triggered_implication
    ADD CONSTRAINT triggered_implication_source_verification_id_fkey FOREIGN KEY (source_verification_id) REFERENCES public.external_evidence_verification_log(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_granted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_granted_by_fkey FOREIGN KEY (granted_by) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: vendors vendors_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- Name: vendors vendors_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: workbook_intake_proposal workbook_intake_proposal_client_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workbook_intake_proposal
    ADD CONSTRAINT workbook_intake_proposal_client_document_id_fkey FOREIGN KEY (client_document_id) REFERENCES public.client_documents(id) ON DELETE SET NULL;


--
-- Name: workbook_intake_proposal workbook_intake_proposal_superseded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workbook_intake_proposal
    ADD CONSTRAINT workbook_intake_proposal_superseded_by_id_fkey FOREIGN KEY (superseded_by_id) REFERENCES public.workbook_intake_proposal(id) ON DELETE SET NULL;


--
-- Name: workbook_intake_proposal workbook_intake_proposal_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workbook_intake_proposal
    ADD CONSTRAINT workbook_intake_proposal_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: ai_call_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.ai_call_log ENABLE ROW LEVEL SECURITY;

--
-- Name: api_keys; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

--
-- Name: api_rate_limit_bucket; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.api_rate_limit_bucket ENABLE ROW LEVEL SECURITY;

--
-- Name: ai_call_log app_ai_call_log_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_ai_call_log_all ON public.ai_call_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: ai_call_log app_all_ai_call_log; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_ai_call_log ON public.ai_call_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: api_keys app_all_api_keys; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_api_keys ON public.api_keys TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: client_documents app_all_client_docs; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_client_docs ON public.client_documents TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: document_text app_all_document_text; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_document_text ON public.document_text TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: document_findings app_all_findings; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_findings ON public.document_findings TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: intake_trace_log app_all_intake_trace; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_intake_trace ON public.intake_trace_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: posture_assertions app_all_posture_assertions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_posture_assertions ON public.posture_assertions TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: posture_status_log app_all_posture_status_log; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_posture_status_log ON public.posture_status_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: tenant_evidence_gaps app_all_tenant_evidence_gaps; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_tenant_evidence_gaps ON public.tenant_evidence_gaps TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: document_uploads app_all_uploads; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_uploads ON public.document_uploads TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: users app_all_users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_users ON public.users TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: workbook_intake_proposal app_all_workbook_intake_proposal; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_all_workbook_intake_proposal ON public.workbook_intake_proposal TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: api_rate_limit_bucket app_api_rate_limit_bucket_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_api_rate_limit_bucket_all ON public.api_rate_limit_bucket TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: chat_casefile_log app_chat_casefile_log_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_chat_casefile_log_all ON public.chat_casefile_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: chat_consensus_log app_chat_consensus_log_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_chat_consensus_log_all ON public.chat_consensus_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: cite_attestation_prompt app_cite_attestation_prompt_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_cite_attestation_prompt_all ON public.cite_attestation_prompt TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: notification_delivery_attempt app_delivery_attempt_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_delivery_attempt_all ON public.notification_delivery_attempt TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: expected_followup_event app_expected_followup_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_expected_followup_all ON public.expected_followup_event TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: external_evidence_source app_external_evidence_source_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_external_evidence_source_all ON public.external_evidence_source TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: fact_recompute_log app_fact_recompute_log_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_fact_recompute_log_all ON public.fact_recompute_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: intake_trace_log app_intake_trace_log_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_intake_trace_log_all ON public.intake_trace_log TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: tenant_notification app_notification_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_notification_all ON public.tenant_notification TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: tenant_notification_channel app_notification_channel_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_notification_channel_all ON public.tenant_notification_channel TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: posture_controls app_posture_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_posture_all ON public.posture_controls TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: risks app_risk_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_risk_all ON public.risks TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: triggered_implication app_triggered_implication_all; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY app_triggered_implication_all ON public.triggered_implication TO arioncomply_app USING (true) WITH CHECK (true);


--
-- Name: applicable_standards; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.applicable_standards ENABLE ROW LEVEL SECURITY;

--
-- Name: assets; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

--
-- Name: audit_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

--
-- Name: cascade_suppression_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cascade_suppression_log ENABLE ROW LEVEL SECURITY;

--
-- Name: chat_casefile_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.chat_casefile_log ENABLE ROW LEVEL SECURITY;

--
-- Name: chat_casefile_log chat_casefile_log_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY chat_casefile_log_tenant_isolation ON public.chat_casefile_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: chat_consensus_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.chat_consensus_log ENABLE ROW LEVEL SECURITY;

--
-- Name: chat_consensus_log chat_consensus_log_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY chat_consensus_log_tenant_isolation ON public.chat_consensus_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: cite_attestation_prompt; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.cite_attestation_prompt ENABLE ROW LEVEL SECURITY;

--
-- Name: cite_attestation_prompt cite_attestation_prompt_tenant_iso; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY cite_attestation_prompt_tenant_iso ON public.cite_attestation_prompt TO arioncomply_app USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true))) WITH CHECK (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: client_documents; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.client_documents ENABLE ROW LEVEL SECURITY;

--
-- Name: client_fact_change_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.client_fact_change_log ENABLE ROW LEVEL SECURITY;

--
-- Name: client_facts; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.client_facts ENABLE ROW LEVEL SECURITY;

--
-- Name: confirmation_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.confirmation_log ENABLE ROW LEVEL SECURITY;

--
-- Name: confirmation_log confirmation_log_tenant; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY confirmation_log_tenant ON public.confirmation_log FOR SELECT USING ((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid));


--
-- Name: control_documents; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.control_documents ENABLE ROW LEVEL SECURITY;

--
-- Name: deletion_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.deletion_log ENABLE ROW LEVEL SECURITY;

--
-- Name: deletion_log deletion_log_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY deletion_log_read ON public.deletion_log FOR SELECT USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) OR (tenant_id IS NULL)));


--
-- Name: document_findings; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.document_findings ENABLE ROW LEVEL SECURITY;

--
-- Name: document_sections; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.document_sections ENABLE ROW LEVEL SECURITY;

--
-- Name: document_text; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.document_text ENABLE ROW LEVEL SECURITY;

--
-- Name: document_uploads; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.document_uploads ENABLE ROW LEVEL SECURITY;

--
-- Name: expected_followup_event; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.expected_followup_event ENABLE ROW LEVEL SECURITY;

--
-- Name: external_evidence_source; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.external_evidence_source ENABLE ROW LEVEL SECURITY;

--
-- Name: external_evidence_verification_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.external_evidence_verification_log ENABLE ROW LEVEL SECURITY;

--
-- Name: fact_recompute_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.fact_recompute_log ENABLE ROW LEVEL SECURITY;

--
-- Name: incident_classifications; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incident_classifications ENABLE ROW LEVEL SECURITY;

--
-- Name: incident_documents; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incident_documents ENABLE ROW LEVEL SECURITY;

--
-- Name: incident_obligations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incident_obligations ENABLE ROW LEVEL SECURITY;

--
-- Name: incident_timeline; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incident_timeline ENABLE ROW LEVEL SECURITY;

--
-- Name: incidents; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;

--
-- Name: intake_consensus_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.intake_consensus_log ENABLE ROW LEVEL SECURITY;

--
-- Name: intake_consensus_log intake_consensus_log_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY intake_consensus_log_tenant_isolation ON public.intake_consensus_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: intake_trace_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.intake_trace_log ENABLE ROW LEVEL SECURITY;

--
-- Name: isms_audits; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.isms_audits ENABLE ROW LEVEL SECURITY;

--
-- Name: notifications; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_must_bridge_coverage pmv_bridge_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY pmv_bridge_tenant_isolation ON public.posture_must_bridge_coverage USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true))) WITH CHECK (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: posture_must_verdicts pmv_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY pmv_tenant_isolation ON public.posture_must_verdicts USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true))) WITH CHECK (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: posture_assertions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_assertions ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_controls; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_controls ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_history; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_history ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_must_bridge_coverage; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_must_bridge_coverage ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_must_verdicts; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_must_verdicts ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_pending; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_pending ENABLE ROW LEVEL SECURITY;

--
-- Name: posture_status_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.posture_status_log ENABLE ROW LEVEL SECURITY;

--
-- Name: ref_sequences; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.ref_sequences ENABLE ROW LEVEL SECURITY;

--
-- Name: remediation_evidence; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.remediation_evidence ENABLE ROW LEVEL SECURITY;

--
-- Name: remediation_plans; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.remediation_plans ENABLE ROW LEVEL SECURITY;

--
-- Name: remediation_tasks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.remediation_tasks ENABLE ROW LEVEL SECURITY;

--
-- Name: request_trace_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.request_trace_log ENABLE ROW LEVEL SECURITY;

--
-- Name: request_trace_log request_trace_log_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY request_trace_log_isolation ON public.request_trace_log FOR SELECT USING ((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid));


--
-- Name: risks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.risks ENABLE ROW LEVEL SECURITY;

--
-- Name: roles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;

--
-- Name: roles roles_read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY roles_read ON public.roles FOR SELECT USING (true);


--
-- Name: tabular_evidence_rows; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tabular_evidence_rows ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_cascade_override; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_cascade_override ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_evidence_gaps; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_evidence_gaps ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_external_system; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_external_system ENABLE ROW LEVEL SECURITY;

--
-- Name: applicable_standards tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.applicable_standards USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: assets tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.assets USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: audit_log tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.audit_log USING ((tenant_id = (current_setting('app.tenant_id'::text, true))::uuid));


--
-- Name: cascade_suppression_log tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.cascade_suppression_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: client_documents tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.client_documents USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: client_fact_change_log tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.client_fact_change_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: client_facts tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.client_facts USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: control_documents tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.control_documents USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: document_findings tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.document_findings USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: document_sections tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.document_sections USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: expected_followup_event tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.expected_followup_event USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: external_evidence_source tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.external_evidence_source USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: external_evidence_verification_log tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.external_evidence_verification_log USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: incident_classifications tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.incident_classifications USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: incident_documents tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.incident_documents USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: incident_obligations tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.incident_obligations USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: incident_timeline tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.incident_timeline USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: incidents tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.incidents USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: isms_audits tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.isms_audits USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: notifications tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.notifications USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: posture_controls tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.posture_controls USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: posture_history tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.posture_history USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: posture_pending tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.posture_pending USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: ref_sequences tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.ref_sequences USING ((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid));


--
-- Name: remediation_evidence tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.remediation_evidence USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: remediation_plans tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.remediation_plans USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: remediation_tasks tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.remediation_tasks USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: risks tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.risks USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: tabular_evidence_rows tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tabular_evidence_rows USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: tenant_cascade_override tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tenant_cascade_override USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: tenant_external_system tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tenant_external_system USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: tenant_notification tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tenant_notification USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: tenant_profile tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tenant_profile USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: tenant_standards tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.tenant_standards USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: triggered_implication tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.triggered_implication USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: user_roles tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.user_roles USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: users tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.users USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: vendors tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation ON public.vendors USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: ai_call_log tenant_isolation_ai_call_log; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_isolation_ai_call_log ON public.ai_call_log USING (((tenant_id IS NULL) OR (tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid)));


--
-- Name: tenant_must_overrides; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_must_overrides ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_notification; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_notification ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_profile; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_profile ENABLE ROW LEVEL SECURITY;

--
-- Name: tenants tenant_self; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_self ON public.tenants USING ((id = (current_setting('app.tenant_id'::text, true))::uuid));


--
-- Name: tenant_source_registry; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_source_registry ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_source_registry tenant_source_registry_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tenant_source_registry_isolation ON public.tenant_source_registry USING (((tenant_id = (NULLIF(current_setting('app.tenant_id'::text, true), ''::text))::uuid) AND (is_active = true)));


--
-- Name: tenant_standards; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenant_standards ENABLE ROW LEVEL SECURITY;

--
-- Name: tenants; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;

--
-- Name: tenant_must_overrides tmo_tenant_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY tmo_tenant_isolation ON public.tenant_must_overrides USING (((tenant_id)::text = current_setting('app.tenant_id'::text, true))) WITH CHECK (((tenant_id)::text = current_setting('app.tenant_id'::text, true)));


--
-- Name: triggered_implication; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.triggered_implication ENABLE ROW LEVEL SECURITY;

--
-- Name: user_roles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: users; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

--
-- Name: vendors; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.vendors ENABLE ROW LEVEL SECURITY;

--
-- Name: workbook_intake_proposal; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.workbook_intake_proposal ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict 1Fyc0JUNnLuDV7qXy6ZYfiLyEJQdz8F2odL6ngkqRoQbVbfiO5ZI2WG1PrKNhAb

