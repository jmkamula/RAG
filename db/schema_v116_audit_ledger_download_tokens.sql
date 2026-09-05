-- schema_v116_audit_ledger_download_tokens.sql
--
-- Ship 119'.c (2026-09-05) — one-time-download URL infrastructure
-- for the auditor's ledger. The tenant admin generates a token in
-- ArionComply, hands the resulting URL to their auditor, and the
-- auditor downloads the ledger without needing an API key.
--
-- Design decisions locked into the schema:
--
--   · DB-backed opaque tokens, not signed JWTs. Reasons: revocable
--     (soft-delete via revoked_at), auditable (access_log inline),
--     no signing key to manage / rotate.
--
--   · Ledger generation parameters (as_of, auditor_firm, redaction
--     level, verbatim-excerpts opt-in, ...) captured at TOKEN
--     creation, not at fetch. Every fetch regenerates the ledger
--     with identical parameters — so what the auditor sees at
--     fetch time is what the tenant committed to at token time,
--     even if underlying state has drifted.
--
--   · times_used counter + max_uses limit. Default is single-use
--     (max_uses=1) — auditor downloads once, then the token is
--     effectively dead. Set max_uses higher for iterative reviews.
--
--   · expires_at is REQUIRED. Default 7 days at the endpoint layer.
--     No indefinite-lifetime tokens.
--
--   · access_log inline JSONB. Records ts + IP + user-agent per
--     fetch. Fine for MVP scale; move to a separate table if
--     retention becomes an issue.
--
--   · Tenant FK ON DELETE NO ACTION. Same discipline as audit
--     tables from Ship 4'.b addendum + Ship 118'.b —
--     compliance-load-bearing evidence never silently disappears.

BEGIN;

CREATE TABLE IF NOT EXISTS public.audit_ledger_download_token (
    token         TEXT PRIMARY KEY,
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE NO ACTION,

    -- Lifecycle
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by    UUID,           -- user_id of the tenant admin who generated it
    expires_at    TIMESTAMPTZ NOT NULL,
    max_uses      INTEGER NOT NULL DEFAULT 1 CHECK (max_uses > 0),
    times_used    INTEGER NOT NULL DEFAULT 0 CHECK (times_used >= 0),
    revoked_at    TIMESTAMPTZ,    -- set by admin to invalidate before natural expiry
    revoked_by    UUID,

    -- Ledger generation parameters (frozen at token creation)
    as_of                     TEXT,      -- ISO date or NULL for "now-at-fetch"
    auditor_firm              TEXT,
    engagement_date           TEXT,
    engagement_reference      TEXT,
    redaction_level           TEXT NOT NULL DEFAULT 'default'
        CHECK (redaction_level IN ('off', 'default', 'strict')),
    include_verbatim_excerpts BOOLEAN NOT NULL DEFAULT FALSE,
    pseudonymise_users        BOOLEAN NOT NULL DEFAULT TRUE,
    retention_days            INTEGER NOT NULL DEFAULT 2555,   -- 7 years

    -- Access log: one entry per fetch
    -- [{ "ts": "...", "ip": "...", "ua": "...", "ledger_id": "..." }, ...]
    access_log    JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Operator annotation
    label         TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_token_tenant_active
    ON public.audit_ledger_download_token (tenant_id, created_at DESC)
    WHERE revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_audit_token_expires
    ON public.audit_ledger_download_token (expires_at)
    WHERE revoked_at IS NULL;

ALTER TABLE public.audit_ledger_download_token ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_audit_token ON public.audit_ledger_download_token;
CREATE POLICY app_all_audit_token
    ON public.audit_ledger_download_token
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

-- App role: read + insert + update (for times_used + access_log
-- increment + revoked_at flip). No DELETE — expired tokens should
-- age out via a future retention sweep, never hard-deleted.
GRANT SELECT, INSERT, UPDATE ON public.audit_ledger_download_token TO arioncomply_app;
REVOKE DELETE ON public.audit_ledger_download_token FROM arioncomply_app;

COMMIT;
