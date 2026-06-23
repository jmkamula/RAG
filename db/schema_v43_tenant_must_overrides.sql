-- schema_v43 — per-tenant MUST applicability overrides.
--
-- A.5.15's `access_control_policy` leaf has 7 MUSTs including
-- `physical_rules` ("physical access rules — premises, server rooms").
-- For a cloud-only tenant (no physical infrastructure in scope), this
-- MUST will never apply. Pre-v43 the engine still counted it as
-- required → leaf math could never reach satisfied; the advisory
-- enumerated "Physical access rules" as a missing item, leaking
-- "physical" into chat answers about access-rights gaps.
--
-- This table lets a tenant declare specific MUSTs as not-applicable.
-- Engine filters them out of the denominator; advisory hides them.
-- Audit trail preserved via reason + set_by + set_at.
--
-- Different from inference_source='workbook'/'form' on document_findings:
-- this isn't an evidence claim, it's a SCOPE declaration ("we don't
-- need to evidence this MUST because our scope excludes the underlying
-- requirement"). Similar shape to GDPR's profile_fact + N/A pattern
-- but applied per-MUST instead of per-control.
--
-- Future direction: tag MUSTs in Neo4j with applies_when expressions
-- (e.g. tenant.physical_scope) so this is curation-driven instead of
-- per-tenant. For MVP, per-tenant overrides are the surgical fix.

CREATE TABLE IF NOT EXISTS tenant_must_overrides (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   uuid NOT NULL,
    must_id     text NOT NULL,
    applies     boolean NOT NULL DEFAULT FALSE,  -- false = N/A for this tenant
    reason      text,
    set_by      uuid,
    set_at      timestamp with time zone NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, must_id)
);

CREATE INDEX IF NOT EXISTS idx_tenant_must_overrides_tenant
    ON tenant_must_overrides(tenant_id);

-- RLS: same pattern as posture_controls / document_findings.
-- arioncomply_app has no BYPASSRLS, so set_config('app.tenant_id', ...)
-- gates every read/write.
ALTER TABLE tenant_must_overrides ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tmo_tenant_isolation ON tenant_must_overrides;
CREATE POLICY tmo_tenant_isolation ON tenant_must_overrides
    FOR ALL
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE))
    WITH CHECK (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_must_overrides TO arioncomply_app;
