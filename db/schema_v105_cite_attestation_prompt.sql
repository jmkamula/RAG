-- schema_v105_cite_attestation_prompt.sql
--
-- Ship 92'.b.i (2026-08-21) — system-attestation cite lifecycle close.
--
-- Ship 92'.a's URL-basename resolver only works when cite URLs are
-- clean file paths. Real tenants use SharePoint, Google Drive,
-- OneDrive, Confluence, Notion — where the filename lives in query
-- params or is absent entirely. Ship 92'.b pivots to the
-- scale-invariant primitive: tenant one-click attestation triggered
-- by MUST-overlap between an uploaded document and an active cite.
--
-- Flow:
--   1. Tenant uploads doc → doc_pipeline → document_findings written
--   2. Ship 92'.b.ii candidate detector scans: for each active
--      cite whose must_id has a `status='present'` finding from
--      this doc → INSERT cite_attestation_prompt (status='pending')
--   3. Tenant sees prompt on dashboard drill-in surface
--   4. Tenant clicks Confirm → writes external_evidence_verification_log
--      + bumps last_verified_at + status='confirmed'
--   5. Tenant clicks Dismiss → status='dismissed' (auditor trail preserved)
--   6. Prompt auto-expires after N days (30d default) if no action
--
-- The critical property: tenant OWNS the match decision. System
-- notices candidates via MUST overlap (auditor-defensible signal);
-- doesn't guess URLs. Scale-invariant across every DMS / cloud-drive
-- URL scheme because we're not parsing URLs.

BEGIN;

CREATE TABLE IF NOT EXISTS cite_attestation_prompt (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id            UUID          NOT NULL REFERENCES tenants(id),
    -- The cite that needs attestation:
    cite_id              UUID          NOT NULL
                                       REFERENCES external_evidence_source(id)
                                       ON DELETE CASCADE,
    -- The candidate document (uploaded, has present finding on same MUST):
    candidate_document_id UUID         NOT NULL
                                       REFERENCES client_documents(id)
                                       ON DELETE CASCADE,
    -- Denormalized for cheap listing + display:
    must_id              TEXT          NOT NULL,
    leaf_id              TEXT          NOT NULL,
    control_ref          TEXT          NOT NULL,

    -- Lifecycle:
    status               TEXT          NOT NULL DEFAULT 'pending',
    -- 'pending' → 'confirmed' | 'dismissed' | 'auto_expired'

    -- Confirmation trail:
    resolved_at          TIMESTAMPTZ,
    resolved_by          UUID,           -- tenant user who acted
    dismissed_reason     TEXT,
    verification_log_id  UUID            -- FK external_evidence_verification_log on confirm
                                        REFERENCES external_evidence_verification_log(id)
                                        ON DELETE SET NULL,

    -- Auto-expire:
    expires_at           TIMESTAMPTZ   NOT NULL DEFAULT (NOW() + INTERVAL '30 days'),

    created_at           TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT cite_attestation_prompt_status_chk CHECK (
        status IN ('pending', 'confirmed', 'dismissed', 'auto_expired')
    ),
    CONSTRAINT cite_attestation_prompt_must_id_format CHECK (
        must_id ~ '^item:[A-Za-z0-9.]+:[a-z0-9_]+$'
    ),
    CONSTRAINT cite_attestation_prompt_leaf_id_format CHECK (
        leaf_id ~ '^req:[A-Za-z0-9.]+:[a-z0-9_]+$'
    ),
    CONSTRAINT cite_attestation_prompt_resolution_consistent CHECK (
        (status = 'pending'   AND resolved_at IS NULL)
        OR (status = 'confirmed'    AND resolved_at IS NOT NULL AND verification_log_id IS NOT NULL)
        OR (status = 'dismissed'    AND resolved_at IS NOT NULL AND dismissed_reason IS NOT NULL)
        OR (status = 'auto_expired' AND resolved_at IS NOT NULL)
    )
);

-- One prompt per (tenant, cite, candidate) — dedup by construction.
-- Re-uploading the same doc against the same cite doesn't spam
-- prompts. Prior confirmed / dismissed prompts stay in place for
-- audit trail; a new prompt with the same triple can be created
-- if the prior one was auto_expired (rare edge case).
CREATE UNIQUE INDEX IF NOT EXISTS
    cite_attestation_prompt_unique_active
    ON cite_attestation_prompt (tenant_id, cite_id, candidate_document_id)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_cite_attestation_prompt_pending
    ON cite_attestation_prompt (tenant_id, created_at DESC)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_cite_attestation_prompt_expires
    ON cite_attestation_prompt (expires_at)
    WHERE status = 'pending';

COMMENT ON TABLE cite_attestation_prompt IS
    'Ship 92''.b — tenant one-click cite attestation. Created on doc '
    'upload when a document has present findings on a MUST that has '
    'an active cite. Tenant confirms via dashboard; confirmation '
    'writes external_evidence_verification_log. Scale-invariant '
    'across URL shapes (SharePoint / Drive / OneDrive / Notion) '
    'because the signal is MUST overlap, not URL parsing.';

-- Table-level grant (arioncomply_app is the app role — no BYPASSRLS).
GRANT SELECT, INSERT, UPDATE, DELETE ON cite_attestation_prompt TO arioncomply_app;

-- Row-level tenant isolation. Both USING (read) and WITH CHECK (write)
-- required — WITH CHECK defaults to reject on INSERT/UPDATE when absent.
ALTER TABLE cite_attestation_prompt ENABLE ROW LEVEL SECURITY;
CREATE POLICY cite_attestation_prompt_tenant_iso
    ON cite_attestation_prompt
    FOR ALL TO arioncomply_app
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE))
    WITH CHECK (tenant_id::text = current_setting('app.tenant_id', TRUE));

COMMIT;
