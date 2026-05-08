-- ArionComply Schema v11 — API Keys + Consultant User
-- Safe to run on top of v10 — no existing tables altered or dropped
--
-- Creates:
--   api_keys table      — API key auth for external access
--   consultant user     — seed user for HITL confirmation
--   arion_api role      — role for API server connections

-- ── API Keys table ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS api_keys (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL REFERENCES tenants(id),
    user_id         UUID        NOT NULL REFERENCES users(id),
    key_hash        TEXT        NOT NULL UNIQUE,   -- SHA-256 of raw key
    key_prefix      TEXT        NOT NULL,          -- first 8 chars for display
    name            TEXT        NOT NULL,          -- e.g. "Arion Consultant Key"
    scopes          TEXT[]      NOT NULL DEFAULT '{chat,hitl,documents,posture}',
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,                   -- NULL = never expires
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      UUID        REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash
    ON api_keys(key_hash) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_api_keys_tenant
    ON api_keys(tenant_id) WHERE is_active = true;

-- RLS
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'api_keys' AND policyname = 'app_all_api_keys'
    ) THEN
        CREATE POLICY app_all_api_keys ON api_keys
            FOR ALL TO arioncomply_app
            USING (true) WITH CHECK (true);
    END IF;
END $$;

GRANT SELECT, INSERT, UPDATE ON api_keys TO arioncomply_app;

-- ── Seed consultant user ──────────────────────────────────────────────────────
INSERT INTO users (tenant_id, email, full_name)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'consultant@arioncomply.com',
    'Arion Consultant'
)
ON CONFLICT (email) DO NOTHING;

-- ── Seed API key for consultant ───────────────────────────────────────────────
-- Raw key: arion_dev_key_2026  (dev only — rotate in production)
-- SHA-256: stored in key_hash
-- Usage:   X-API-Key: arion_dev_key_2026
INSERT INTO api_keys (
    tenant_id,
    user_id,
    key_hash,
    key_prefix,
    name,
    scopes
)
SELECT
    '00000000-0000-0000-0000-000000000001',
    u.id,
    encode(sha256('arion_dev_key_2026'::bytea), 'hex'),
    'arion_de',
    'Arion Dev Key (rotate in production)',
    '{chat,hitl,documents,posture}'
FROM users u
WHERE u.email = 'consultant@arioncomply.com'
ON CONFLICT (key_hash) DO NOTHING;

