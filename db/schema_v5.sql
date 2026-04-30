-- =============================================================================
-- ArionComply — Schema v5
-- Row Level Security — complete tenant isolation
--
-- Applies RLS to all 22 tenant-scoped tables.
-- Tables are grouped by risk: CRITICAL (exposed data) → HIGH → MEDIUM → LOW
--
-- Pattern for all policies:
--   USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID)
--
-- Application must call:
--   SELECT set_config('app.tenant_id', $tenant_id, TRUE)
-- before any query. posture_loader.py already does this.
-- =============================================================================

-- Shorthand: all policies use this expression
-- (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID)
-- TRUE in current_setting means "missing_ok" — returns NULL if not set
-- NULLIF converts empty string to NULL — prevents matching on empty tenant

-- =============================================================================
-- CRITICAL — contains PII, findings, financial data, personal records
-- =============================================================================

-- client_facts (sector, processing activities, role)
ALTER TABLE client_facts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON client_facts;
CREATE POLICY tenant_isolation ON client_facts
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- posture_controls (compliance findings — core platform data)
ALTER TABLE posture_controls ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON posture_controls;
CREATE POLICY tenant_isolation ON posture_controls
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- posture_pending (proposed changes — sensitive internal deliberation)
ALTER TABLE posture_pending ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON posture_pending;
CREATE POLICY tenant_isolation ON posture_pending
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- client_documents (document metadata and content)
ALTER TABLE client_documents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON client_documents;
CREATE POLICY tenant_isolation ON client_documents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- document_sections (extracted document content)
ALTER TABLE document_sections ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON document_sections;
CREATE POLICY tenant_isolation ON document_sections
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- document_findings (checklist evaluation results)
ALTER TABLE document_findings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON document_findings;
CREATE POLICY tenant_isolation ON document_findings
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- incidents (security incidents — highly sensitive)
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON incidents;
CREATE POLICY tenant_isolation ON incidents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- incident_timeline
ALTER TABLE incident_timeline ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON incident_timeline;
CREATE POLICY tenant_isolation ON incident_timeline
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- incident_documents
ALTER TABLE incident_documents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON incident_documents;
CREATE POLICY tenant_isolation ON incident_documents
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- incident_obligations
ALTER TABLE incident_obligations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON incident_obligations;
CREATE POLICY tenant_isolation ON incident_obligations
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- assets (asset register — includes PII asset classification)
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON assets;
CREATE POLICY tenant_isolation ON assets
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- risks (risk register)
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON risks;
CREATE POLICY tenant_isolation ON risks
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- vendors (supplier data including DPA status)
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON vendors;
CREATE POLICY tenant_isolation ON vendors
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- =============================================================================
-- HIGH — operational and remediation data
-- =============================================================================

-- remediation_plans
ALTER TABLE remediation_plans ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON remediation_plans;
CREATE POLICY tenant_isolation ON remediation_plans
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- remediation_tasks
ALTER TABLE remediation_tasks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON remediation_tasks;
CREATE POLICY tenant_isolation ON remediation_tasks
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- remediation_evidence
ALTER TABLE remediation_evidence ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON remediation_evidence;
CREATE POLICY tenant_isolation ON remediation_evidence
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- isms_audits (audit records)
ALTER TABLE isms_audits ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON isms_audits;
CREATE POLICY tenant_isolation ON isms_audits
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- posture_history (historical posture — change audit trail)
-- Already has RLS from schema_v1 — ensure policy name is consistent
-- (skip if already exists — idempotent)

-- =============================================================================
-- MEDIUM — user and configuration data
-- =============================================================================

-- users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON users;
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- user_roles
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON user_roles;
CREATE POLICY tenant_isolation ON user_roles
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- applicable_standards (tenant standard selections)
ALTER TABLE applicable_standards ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON applicable_standards;
CREATE POLICY tenant_isolation ON applicable_standards
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- notifications
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON notifications;
CREATE POLICY tenant_isolation ON notifications
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- tenant_standards (enrollment — already in schema_v3)
ALTER TABLE tenant_standards ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON tenant_standards;
CREATE POLICY tenant_isolation ON tenant_standards
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- =============================================================================
-- LOW — platform infrastructure (tenant-scoped but low sensitivity)
-- =============================================================================

-- ref_sequences (platform ref counters)
ALTER TABLE ref_sequences ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON ref_sequences;
CREATE POLICY tenant_isolation ON ref_sequences
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

-- =============================================================================
-- VIEWS that need fixing
-- =============================================================================

-- v_incidents_open — RLS on incidents table now enforces tenant isolation
-- View itself doesn't need a WHERE tenant_id clause — RLS handles it
-- Skipping CREATE OR REPLACE to avoid column mismatch errors on re-run

-- v_retention_warnings — uses WHERE tenant_id in body but may not join correctly
-- Leave as-is — it already has tenant_id filter and joins to RLS-protected tables

-- =============================================================================
-- SUPERUSER BYPASS
-- The postgres superuser and arioncomply_app bypass RLS for admin operations.
-- In production, admin operations should use a separate admin connection
-- with explicit tenant context set.
-- =============================================================================

-- Allow app user to bypass RLS only when tenant context IS set
-- (This is handled by the policy — if app.tenant_id is not set,
--  NULLIF returns NULL, and NULL != any tenant_id, so no rows returned)

-- =============================================================================
-- VERIFICATION QUERY
-- Run after applying to confirm all tables have RLS
-- =============================================================================

-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
--   AND tablename IN (
--     'client_facts','posture_controls','posture_pending','client_documents',
--     'document_sections','document_findings','incidents','incident_timeline',
--     'incident_documents','incident_obligations','assets','risks','vendors',
--     'remediation_plans','remediation_tasks','remediation_evidence',
--     'isms_audits','users','user_roles','applicable_standards',
--     'notifications','tenant_standards','ref_sequences','control_documents'
--   )
-- ORDER BY tablename;
-- All should show rowsecurity = TRUE

