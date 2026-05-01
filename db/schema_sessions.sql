-- =============================================================================
-- ArionComply — Sessions Database
-- arioncomply_sessions
--
-- Separate from arioncomply_compliance by design:
--   compliance: 3-7 year retention, auditable, backup-critical
--   sessions:   90-day retention, reconstructible, purge-safe
--
-- Run as superuser against arioncomply_sessions database:
--   psql arioncomply_sessions < schema_sessions.sql
-- =============================================================================


-- =============================================================================
-- SECTION 1: DATABASE + USER SETUP
-- (run as postgres superuser if database doesn't exist yet)
-- =============================================================================

-- Create database if needed (run outside transaction):
-- CREATE DATABASE arioncomply_sessions;

-- Create app user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arioncomply_app') THEN
        CREATE ROLE arioncomply_app LOGIN PASSWORD 'arionlocal2026';
    END IF;
END $$;

-- Grant connect
GRANT CONNECT ON DATABASE arioncomply_sessions TO arioncomply_app;
GRANT USAGE ON SCHEMA public TO arioncomply_app;
GRANT CREATE ON SCHEMA public TO arioncomply_app;


-- =============================================================================
-- SECTION 2: LANGGRAPH CHECKPOINT TABLES
-- Required by PostgresSaver for conversation state persistence.
-- These are LangGraph's internal tables — schema matches what saver.setup() creates.
-- =============================================================================

CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id           TEXT        NOT NULL,
    checkpoint_ns       TEXT        NOT NULL DEFAULT '',
    checkpoint_id       TEXT        NOT NULL,
    parent_checkpoint_id TEXT,
    type                TEXT,
    checkpoint          JSONB       NOT NULL,
    metadata            JSONB       NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id       TEXT    NOT NULL,
    checkpoint_ns   TEXT    NOT NULL DEFAULT '',
    channel         TEXT    NOT NULL,
    version         TEXT    NOT NULL,
    type            TEXT    NOT NULL,
    blob            BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id       TEXT    NOT NULL,
    checkpoint_ns   TEXT    NOT NULL DEFAULT '',
    checkpoint_id   TEXT    NOT NULL,
    task_id         TEXT    NOT NULL,
    idx             INTEGER NOT NULL,
    channel         TEXT    NOT NULL,
    type            TEXT,
    blob            BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- Indexes for common access patterns
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
    ON checkpoints (thread_id, checkpoint_ns, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_checkpoint_blobs_thread
    ON checkpoint_blobs (thread_id, checkpoint_ns);

CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread
    ON checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id);


-- =============================================================================
-- SECTION 3: SESSION METADATA
-- ArionComply-specific session tracking — not part of LangGraph schema.
-- Links thread_id to tenant_id and tracks session lifecycle.
-- =============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id       TEXT        NOT NULL UNIQUE,  -- LangGraph thread_id
    tenant_id       UUID        NOT NULL,          -- links to arioncomply_compliance.tenants
    user_id         UUID,                          -- optional user within tenant
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    turn_count      INT         NOT NULL DEFAULT 0,
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '90 days',
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_sessions_tenant
    ON sessions (tenant_id, last_active_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_expires
    ON sessions (expires_at) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_sessions_thread
    ON sessions (thread_id);


-- =============================================================================
-- SECTION 4: CONVERSATION HISTORY
-- Full conversation log — separate from LangGraph checkpoints.
-- LangGraph checkpoints = pipeline state (internal).
-- conversation_history = human-readable audit trail (business-facing).
-- =============================================================================

CREATE TABLE IF NOT EXISTS conversation_history (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID        NOT NULL REFERENCES sessions(id),
    tenant_id       UUID        NOT NULL,
    thread_id       TEXT        NOT NULL,
    turn_number     INT         NOT NULL,
    role            TEXT        NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT        NOT NULL,
    question_type   TEXT,       -- gap_analysis | implementation | definition | ...
    cited_refs      TEXT[],     -- ISO control refs cited in the answer
    answer_source   TEXT,       -- llm | postgres
    latency_ms      INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_history_session
    ON conversation_history (session_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_conv_history_tenant
    ON conversation_history (tenant_id, created_at DESC);


-- =============================================================================
-- SECTION 5: RETENTION — 90-DAY AUTO-PURGE
-- Sessions and conversation history are not compliance evidence.
-- They can be reconstructed from LangGraph checkpoints if needed.
-- Auto-purge after 90 days (configurable per tenant in future).
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_purge_expired_sessions(
    p_dry_run BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    table_name      TEXT,
    records_purged  BIGINT
) AS $$
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
$$ LANGUAGE plpgsql;


-- =============================================================================
-- SECTION 6: GRANTS
-- arioncomply_app: full access to session data
-- No other roles needed — sessions DB is ArionComply system only
-- =============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE
    ON checkpoints, checkpoint_blobs, checkpoint_writes,
       sessions, conversation_history
    TO arioncomply_app;

GRANT EXECUTE ON FUNCTION fn_purge_expired_sessions(BOOLEAN) TO arioncomply_app;

-- Grant on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arioncomply_app;


-- =============================================================================
-- VERIFY
-- =============================================================================
SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

