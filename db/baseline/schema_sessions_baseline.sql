-- ArionComply — Postgres schema baseline (arioncomply_sessions)
-- Generated: 2026-09-05T17:33:48Z from HEAD 778d7dcc by scripts/build_pg_baseline.sh
-- LangGraph checkpointer schema. Zero session data.

--
-- PostgreSQL database dump
--

\restrict HvzyVQVpJ0oEvUPtuX5m0errwNkDDjKrxZ9bApnRGNmnjDyxxs63l5XGBuiUUy1

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
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: fn_checkpoints_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_checkpoints_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;


--
-- Name: fn_purge_expired_sessions(boolean); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_purge_expired_sessions(p_dry_run boolean DEFAULT true) RETURNS TABLE(table_name text, records_purged bigint)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_count BIGINT;
BEGIN
    -- Count/purge conversation history for expired sessions
    IF p_dry_run THEN
        SELECT count(*) INTO v_count
        FROM conversation_history ch
        JOIN sessions s ON s.id = ch.session_id
        WHERE s.expires_at < NOW();
    ELSE
        DELETE FROM conversation_history
        WHERE session_id IN (
            SELECT id FROM sessions WHERE expires_at < NOW()
        );
        GET DIAGNOSTICS v_count = ROW_COUNT;
    END IF;
    table_name := 'conversation_history'; records_purged := v_count;
    RETURN NEXT;

    -- Count/purge expired checkpoint data
    IF p_dry_run THEN
        SELECT count(*) INTO v_count
        FROM checkpoints c
        JOIN sessions s ON s.thread_id = c.thread_id
        WHERE s.expires_at < NOW();
    ELSE
        DELETE FROM checkpoint_blobs
        WHERE thread_id IN (
            SELECT thread_id FROM sessions WHERE expires_at < NOW()
        );
        DELETE FROM checkpoint_writes
        WHERE thread_id IN (
            SELECT thread_id FROM sessions WHERE expires_at < NOW()
        );
        DELETE FROM checkpoints
        WHERE thread_id IN (
            SELECT thread_id FROM sessions WHERE expires_at < NOW()
        );
        GET DIAGNOSTICS v_count = ROW_COUNT;
    END IF;
    table_name := 'checkpoints'; records_purged := v_count;
    RETURN NEXT;

    -- Purge the sessions themselves last
    IF NOT p_dry_run THEN
        DELETE FROM sessions WHERE expires_at < NOW();
        GET DIAGNOSTICS v_count = ROW_COUNT;
    ELSE
        SELECT count(*) INTO v_count FROM sessions WHERE expires_at < NOW();
    END IF;
    table_name := 'sessions'; records_purged := v_count;
    RETURN NEXT;
END;
$$;


--
-- Name: fn_purge_old_sessions(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_purge_old_sessions(retention_days integer DEFAULT 90) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE deleted int;
BEGIN
    DELETE FROM checkpoints
    WHERE updated_at < NOW() - (retention_days || chr(32) || 'days')::interval;
    GET DIAGNOSTICS deleted = ROW_COUNT;
    RETURN deleted;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: checkpoint_blobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_blobs (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    channel text NOT NULL,
    version text NOT NULL,
    type text NOT NULL,
    blob bytea
);


--
-- Name: checkpoint_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_migrations (
    v integer NOT NULL
);


--
-- Name: checkpoint_writes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoint_writes (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    idx integer NOT NULL,
    channel text NOT NULL,
    type text,
    blob bytea,
    task_path text DEFAULT ''::text NOT NULL
);


--
-- Name: checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.checkpoints (
    thread_id text NOT NULL,
    checkpoint_ns text DEFAULT ''::text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    type text,
    checkpoint jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversation_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    thread_id text NOT NULL,
    turn_number integer NOT NULL,
    role text NOT NULL,
    content text NOT NULL,
    question_type text,
    cited_refs text[],
    answer_source text,
    latency_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT conversation_history_role_check CHECK ((role = ANY (ARRAY['user'::text, 'assistant'::text, 'system'::text])))
);


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    thread_id text NOT NULL,
    tenant_id uuid NOT NULL,
    user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_active_at timestamp with time zone DEFAULT now() NOT NULL,
    turn_count integer DEFAULT 0 NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '90 days'::interval) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: checkpoint_blobs checkpoint_blobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_blobs
    ADD CONSTRAINT checkpoint_blobs_pkey PRIMARY KEY (thread_id, checkpoint_ns, channel, version);


--
-- Name: checkpoint_migrations checkpoint_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_migrations
    ADD CONSTRAINT checkpoint_migrations_pkey PRIMARY KEY (v);


--
-- Name: checkpoint_writes checkpoint_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoint_writes
    ADD CONSTRAINT checkpoint_writes_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx);


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id);


--
-- Name: conversation_history conversation_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_history
    ADD CONSTRAINT conversation_history_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_thread_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_thread_id_key UNIQUE (thread_id);


--
-- Name: idx_checkpoints_updated_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_checkpoints_updated_at ON public.checkpoints USING btree (updated_at);


--
-- Name: idx_conv_history_session; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conv_history_session ON public.conversation_history USING btree (session_id, turn_number);


--
-- Name: idx_conv_history_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conv_history_tenant ON public.conversation_history USING btree (tenant_id, created_at DESC);


--
-- Name: idx_sessions_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sessions_expires ON public.sessions USING btree (expires_at) WHERE (is_active = true);


--
-- Name: idx_sessions_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sessions_tenant ON public.sessions USING btree (tenant_id, last_active_at DESC);


--
-- Name: idx_sessions_thread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sessions_thread ON public.sessions USING btree (thread_id);


--
-- Name: checkpoints trg_checkpoints_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_checkpoints_updated_at BEFORE INSERT OR UPDATE ON public.checkpoints FOR EACH ROW EXECUTE FUNCTION public.fn_checkpoints_updated_at();


--
-- Name: conversation_history conversation_history_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_history
    ADD CONSTRAINT conversation_history_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id);


--
-- PostgreSQL database dump complete
--

\unrestrict HvzyVQVpJ0oEvUPtuX5m0errwNkDDjKrxZ9bApnRGNmnjDyxxs63l5XGBuiUUy1

