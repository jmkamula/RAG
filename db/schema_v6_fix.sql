-- =============================================================================
-- Schema v6 fix: retention_policies table had wrong column names from
-- an earlier version. Drop and recreate with correct schema.
-- =============================================================================

-- Drop the old table (safe — no FK dependencies on it yet)
DROP TABLE IF EXISTS retention_policies CASCADE;

-- Recreate with correct column names
CREATE TABLE retention_policies (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id             UUID REFERENCES tenants(id),  -- NULL = platform default
    retention_class       TEXT NOT NULL,
    table_name            TEXT,                          -- NULL = class-level default
    retain_years          INT  NOT NULL DEFAULT 0,
    retain_days           INT  NOT NULL DEFAULT 0,
    anonymise_after_years INT,
    auto_purge            BOOLEAN NOT NULL DEFAULT FALSE,
    legal_basis           TEXT NOT NULL,
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial unique index (NULL tenant_id = platform default)
CREATE UNIQUE INDEX idx_retention_policies_default
    ON retention_policies (retention_class, COALESCE(table_name, ''))
    WHERE tenant_id IS NULL;

-- Platform defaults
INSERT INTO retention_policies
    (retention_class, table_name, retain_years, retain_days,
     anonymise_after_years, auto_purge, legal_basis, notes)
VALUES
    ('compliance', NULL,                7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(e)',
     'Compliance records retained 7 years, manual review before purge'),
    ('compliance', 'posture_controls',  7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Posture history required for audit trail'),
    ('compliance', 'isms_audits',       7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Audit records required for surveillance audits'),
    ('compliance', 'incidents',         7, 0, 5,     FALSE,
     'ISO 27001 A.5.26, GDPR Art.33',
     'Anonymise personal data after 5 years, retain incident record for 7'),
    ('compliance', 'document_findings', 7, 0, NULL,  FALSE,
     'ISO 27001 A.5.33', 'Evidence of document evaluation retained'),
    ('operational', NULL,               5, 0, 3,     TRUE,
     'ISO 27001 A.5.33, GDPR Art.5(1)(e)',
     'Operational records 5 years, PII anonymised after 3'),
    ('operational', 'risks',            5, 0, 3,     TRUE,
     'ISO 27001 A.5.33', 'Risk register retained 5 years'),
    ('operational', 'vendors',          5, 0, 3,     TRUE,
     'ISO 27001 A.5.33, GDPR Art.28',
     'Processor agreements 5 years, contact data anonymised at 3'),
    ('operational', 'remediation_plans',5, 0, NULL,  TRUE,
     'ISO 27001 A.5.33', 'Remediation evidence retained 5 years'),
    ('personal_data', NULL,             0, 0, NULL,  FALSE,
     'GDPR Art.17', 'Erasure on data subject request within 30 days'),
    ('personal_data', 'users',          0, 0, NULL,  FALSE,
     'GDPR Art.17', 'User accounts anonymised on erasure request'),
    ('platform', NULL,                  0, 30, NULL, TRUE,
     'Contractual', 'Soft deleted on tenant offboarding, purged after 30 days'),
    ('session', NULL,                   0, 90, NULL, TRUE,
     'GDPR Art.5(1)(e)', 'Conversation history auto-purged after 90 days');

GRANT SELECT, INSERT, UPDATE ON retention_policies TO arioncomply_app;

-- Verify
SELECT retention_class,
       COALESCE(table_name, '(all)') AS applies_to,
       retain_years,
       retain_days,
       auto_purge,
       legal_basis
FROM retention_policies
WHERE tenant_id IS NULL
ORDER BY retention_class, table_name NULLS FIRST;

