-- schema_v49: tenant_profile — key/value store for template-substitution
-- placeholders that aren't core tenant identity (name/country/sector).
--
-- The renderer already substitutes <<TENANT_NAME>>, <<TENANT_COUNTRY>>,
-- <<TENANT_SECTOR>>, <<TENANT_INDUSTRY>>, <<GENERATED_DATE>> from the
-- `tenants` table. But templates use ~15+ other placeholders that
-- depend on tenant-specific people / addresses / dates we don't store
-- in `tenants`:
--
--   <<CEO_NAME>>, <<CISO_NAME>>, <<DPO_NAME>>, <<ISMS_MANAGER_NAME>>,
--   <<ISMS_OWNER_NAME>>, <<HR_PARTNER_NAME>>, <<AWARENESS_LEAD_NAME>>,
--   <<REGISTERED_ADDRESS>>, <<COMPANY_NUMBER>>, <<TENANT_DOMAIN>>,
--   <<PRODUCT_OR_SERVICE>>, <<APPROVAL_DATE>>, <<NEXT_REVIEW_DATE>>
--
-- Without these, downloaded templates leak literal `<<CEO_NAME>>` text
-- the tenant has to find + edit by hand in every document. With this
-- table, the renderer reads key/value pairs and extends the
-- substitution map → tenant types once per organisation, renders
-- everywhere.
--
-- Key/value shape (vs adding columns to `tenants`) because the
-- placeholder set is open-ended — new templates may introduce new
-- placeholders without schema migrations.
--
-- profile_key normalised to lowercase + underscored slug — same
-- transform the renderer applies to the placeholder name. e.g.
--   <<ISMS_MANAGER_NAME>>  ↔  profile_key='isms_manager_name'

BEGIN;

CREATE TABLE IF NOT EXISTS tenant_profile (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID         NOT NULL,
    profile_key   TEXT         NOT NULL,
    profile_value TEXT         NOT NULL DEFAULT '',
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_by    UUID,
    CONSTRAINT tenant_profile_unique_per_tenant UNIQUE (tenant_id, profile_key),
    CONSTRAINT tenant_profile_key_format
        CHECK (profile_key ~ '^[a-z][a-z0-9_]*$')
);

CREATE INDEX IF NOT EXISTS idx_tenant_profile_tenant
    ON tenant_profile(tenant_id);

ALTER TABLE tenant_profile ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON tenant_profile;
CREATE POLICY tenant_isolation ON tenant_profile
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_profile TO arioncomply_app;

COMMENT ON TABLE  tenant_profile IS
    'Key/value store for template-substitution placeholders. Keyed by tenant_id + profile_key (lowercase_with_underscores).';
COMMENT ON COLUMN tenant_profile.profile_key IS
    'Placeholder name with the <<>> wrapping removed and lowercased: <<CEO_NAME>> → ceo_name';

COMMIT;
