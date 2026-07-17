-- ArionComply Schema v9 — Registration + Document Uploads
-- Adds: tenants (extended), users, document_uploads, document_findings
-- Safe to run on top of v8 — uses CREATE TABLE IF NOT EXISTS

-- ── Tenants (extended) ────────────────────────────────────────────────────────
ALTER TABLE tenants
  ADD COLUMN IF NOT EXISTS industry              TEXT,
  ADD COLUMN IF NOT EXISTS employee_count        INTEGER,
  ADD COLUMN IF NOT EXISTS has_physical_premises BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS does_software_development BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS cloud_only            BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS onboarding_status     TEXT DEFAULT 'registered'
    CHECK (onboarding_status IN ('registered','assessed','active'));

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID        NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email          TEXT        NOT NULL,
  role           TEXT        NOT NULL DEFAULT 'viewer'
    CHECK (role IN ('owner','admin','consultant','viewer')),
  password_hash  TEXT,
  phone          TEXT,
  job_title      TEXT,
  is_primary     BOOLEAN     DEFAULT FALSE,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tenant_id, email)
);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);

-- ── Document Uploads ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_uploads (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID        NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  filename           TEXT        NOT NULL,
  storage_path       TEXT,
  doc_type           TEXT,
  standard_ids       TEXT[],
  extraction_path    TEXT        CHECK (extraction_path IN
                                   ('full_document','section_based','structured','manual_review')),
  extraction_status  TEXT        NOT NULL DEFAULT 'pending'
    CHECK (extraction_status IN ('pending','processing','completed','failed','manual_review')),
  findings_count     INTEGER     DEFAULT 0,
  token_estimate     INTEGER,
  error_message      TEXT,
  uploaded_by        UUID        REFERENCES users(id),
  uploaded_at        TIMESTAMPTZ DEFAULT now(),
  processed_at       TIMESTAMPTZ,
  created_at         TIMESTAMPTZ DEFAULT now(),
  updated_at         TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_doc_uploads_tenant    ON document_uploads(tenant_id);
CREATE INDEX IF NOT EXISTS idx_doc_uploads_status    ON document_uploads(extraction_status);

-- ── Document Findings ─────────────────────────────────────────────────────────
-- Ship 2'.r (2026-07-17): the CREATE TABLE block that used to live here
-- was a phantom — schema.sql (v1) had already created `document_findings`
-- with a different shape (document_id FK to client_documents, `status`
-- enum, `checklist_item_id`, etc). The `IF NOT EXISTS` on the phantom
-- caused it to silently no-op; downstream code never used the columns
-- proposed here (`upload_id`, `compliance_status`, `evidence_excerpt`,
-- `source_section`) and the phantom index `idx_doc_findings_upload`
-- errored out silently at load time (no such column).
--
-- The CANONICAL `document_findings` definition lives in `db/schema.sql`
-- + subsequent migrations. Do not add a competing definition here.
--
-- The two indexes below (idx_doc_findings_tenant + idx_doc_findings_control)
-- DID take effect (columns exist) and are preserved to stay idempotent
-- with what's currently in the live database.
CREATE INDEX IF NOT EXISTS idx_doc_findings_tenant   ON document_findings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_doc_findings_control  ON document_findings(control_ref);
-- (idx_doc_findings_upload was never created — column doesn't exist.)

-- Enable RLS
ALTER TABLE document_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Permissive policies for arioncomply_app.
-- Ship 2'.r (2026-07-17): PostgreSQL doesn't support `CREATE POLICY
-- IF NOT EXISTS` — the previous `IF NOT EXISTS` was invalid syntax
-- that errored silently on every re-run. Use DROP + CREATE for
-- idempotency (the tenant_isolation policy from schema.sql stays
-- untouched; these are additive).
DROP POLICY IF EXISTS app_all_uploads  ON document_uploads;
CREATE POLICY app_all_uploads  ON document_uploads
  FOR ALL TO arioncomply_app USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS app_all_findings ON document_findings;
CREATE POLICY app_all_findings ON document_findings
  FOR ALL TO arioncomply_app USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS app_all_users ON users;
CREATE POLICY app_all_users ON users
  FOR ALL TO arioncomply_app USING (true) WITH CHECK (true);

-- Grants
GRANT SELECT, INSERT, UPDATE, DELETE ON document_uploads  TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON document_findings TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users             TO arioncomply_app;

-- ── Registration status view ──────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_registration_status AS
SELECT
  t.id                                          AS tenant_id,
  t.name                                        AS tenant_name,
  t.onboarding_status,
  COUNT(DISTINCT u.id)                          AS user_count,
  COUNT(DISTINCT ts.id)                         AS standards_count,
  COUNT(DISTINCT pc.id)                         AS posture_controls,
  COUNT(DISTINCT du.id)                         AS documents_uploaded,
  CASE
    WHEN COUNT(DISTINCT u.id) > 0
     AND COUNT(DISTINCT ts.id) > 0
     AND COUNT(DISTINCT pc.id) > 0 THEN 100
    WHEN COUNT(DISTINCT ts.id) > 0 THEN 50
    ELSE 20
  END                                           AS onboarding_score
FROM tenants t
LEFT JOIN users             u  ON u.tenant_id  = t.id
LEFT JOIN tenant_standards  ts ON ts.tenant_id = t.id
LEFT JOIN posture_controls  pc ON pc.tenant_id = t.id
LEFT JOIN document_uploads  du ON du.tenant_id = t.id
GROUP BY t.id, t.name, t.onboarding_status;

GRANT SELECT ON v_registration_status TO arioncomply_app;

