-- =============================================================================
-- schema_v18_document_text.sql
--
-- Preserve uploaded documents + persist their parsed markdown.
--
-- Two parallel goals:
--   1. Originals: chain-of-custody groundwork. Add sha256 + byte_size to
--      document_uploads so we can prove a stored file matches what was uploaded.
--   2. Parsed text: new document_text table holds the normalized markdown the
--      extractor saw. Lets us replay extraction and serve an audit-readable
--      evidence trail without re-fetching the original binary.
--
-- One document_text row per upload (PK = upload_id). Re-parsing replaces the
-- row in place; a history table is a follow-up if/when re-parsing becomes a
-- regular flow.
-- =============================================================================

BEGIN;

-- ── document_uploads: chain-of-custody columns ───────────────────────────────
ALTER TABLE document_uploads
    ADD COLUMN IF NOT EXISTS sha256    text,
    ADD COLUMN IF NOT EXISTS byte_size integer;

-- ── document_text ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_text (
    upload_id        uuid PRIMARY KEY
                          REFERENCES document_uploads(id) ON DELETE CASCADE,
    tenant_id        uuid NOT NULL
                          REFERENCES tenants(id) ON DELETE CASCADE,
    markdown         text NOT NULL,
    markdown_sha256  text NOT NULL,
    source_sha256    text NOT NULL,    -- sha of the binary we converted from
    converter        text NOT NULL,    -- e.g. 'mammoth/1.12.0'
    byte_count       integer NOT NULL, -- length(markdown) in bytes
    parsed_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_document_text_tenant_time
    ON document_text (tenant_id, parsed_at DESC);

-- RLS — same pattern as intake_trace_log: arioncomply_app sees all, RLS still
-- enforced at the app layer by set_config('app.tenant_id', ...). Superuser
-- (arioncomply) bypasses.
ALTER TABLE document_text ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS app_all_document_text ON document_text;
CREATE POLICY app_all_document_text ON document_text
    FOR ALL
    TO arioncomply_app
    USING (true)
    WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE, DELETE ON document_text TO arioncomply_app;

COMMIT;
