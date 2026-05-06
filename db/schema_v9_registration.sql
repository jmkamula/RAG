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
CREATE TABLE IF NOT EXISTS document_findings (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID        NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  upload_id          UUID        REFERENCES document_uploads(id) ON DELETE SET NULL,
  control_ref        TEXT        NOT NULL,
  standard_id        TEXT        NOT NULL,
  compliance_status  TEXT        NOT NULL
    CHECK (compliance_status IN ('Comply','NC','OFI','N/A')),
  confidence         TEXT        CHECK (confidence IN ('high','medium','low')),
  evidence_excerpt   TEXT,
  source_section     TEXT,
  created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_doc_findings_tenant   ON document_findings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_doc_findings_control  ON document_findings(control_ref);
CREATE INDEX IF NOT EXISTS idx_doc_findings_upload   ON document_findings(upload_id);

-- Enable RLS
ALTER TABLE document_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Permissive policies for arioncomply_app
CREATE POLICY IF NOT EXISTS app_all_uploads  ON document_uploads
  FOR ALL TO arioncomply_app USING (true) WITH CHECK (true);

CREATE POLICY IF NOT EXISTS app_all_findings ON document_findings
  FOR ALL TO arioncomply_app USING (true) WITH CHECK (true);

CREATE POLICY IF NOT EXISTS app_all_users ON users
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

