-- =============================================================================
-- ArionComply — Schema v2 additions
-- Run after schema.sql — adds tables and columns revealed by workbook import
-- Idempotent: all statements use IF NOT EXISTS / ADD COLUMN IF NOT EXISTS
-- Order: new tables first, then FKs and column additions that reference them
-- =============================================================================

-- =============================================================================
-- SECTION 1: NEW TABLES (no dependencies on existing tables except tenants)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- assets: the asset register (A001-A012 etc)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assets (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(id),
    external_ref            TEXT NOT NULL,
    name                    TEXT NOT NULL,
    asset_type              TEXT,
    owner_text              TEXT,
    owner                   UUID REFERENCES users(id),
    location                TEXT,
    value_classification    TEXT
        CHECK (value_classification IN ('High','Medium','Low') OR value_classification IS NULL),
    cia_c                   TEXT CHECK (cia_c IN ('High','Medium','Low') OR cia_c IS NULL),
    cia_i                   TEXT CHECK (cia_i IN ('High','Medium','Low') OR cia_i IS NULL),
    cia_a                   TEXT CHECK (cia_a IN ('High','Medium','Low') OR cia_a IS NULL),
    comments                TEXT,
    personal_data_types     TEXT[],
    data_subject_categories TEXT[],
    processing_purposes     TEXT[],
    retention_period        TEXT,
    contains_pii            BOOLEAN NOT NULL DEFAULT FALSE,
    workbook_imported       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, external_ref)
);

CREATE INDEX IF NOT EXISTS idx_assets_tenant ON assets (tenant_id);
CREATE INDEX IF NOT EXISTS idx_assets_pii    ON assets (tenant_id, contains_pii)
    WHERE contains_pii = TRUE;

-- -----------------------------------------------------------------------------
-- risks: the risk register (R001-R052 etc)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risks (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id            UUID NOT NULL REFERENCES tenants(id),
    external_ref         TEXT NOT NULL,
    asset_id             UUID REFERENCES assets(id) ON DELETE SET NULL,
    asset_ref            TEXT,
    asset_name           TEXT,
    interested_party     TEXT,
    threat               TEXT,
    vulnerability        TEXT,
    likelihood           INT CHECK (likelihood BETWEEN 1 AND 5),
    impact               INT CHECK (impact BETWEEN 1 AND 5),
    risk_score           INT,
    risk_owner_text      TEXT,
    risk_owner           UUID REFERENCES users(id),
    treatment_option     TEXT
        CHECK (treatment_option IN ('Mitigate','Accept','Transfer','Avoid')
               OR treatment_option IS NULL),
    treatment_action     TEXT,
    isms_controls        TEXT[],
    pims_controls        TEXT[],
    implementation_date  DATE,
    residual_risk_level  INT CHECK (residual_risk_level BETWEEN 1 AND 25),
    treatment_status     TEXT
        CHECK (treatment_status IN ('open','in_progress','implemented','accepted')
               OR treatment_status IS NULL),
    review_date          DATE,
    effectiveness_review TEXT,
    workbook_imported    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, external_ref)
);

CREATE INDEX IF NOT EXISTS idx_risks_tenant ON risks (tenant_id);
CREATE INDEX IF NOT EXISTS idx_risks_asset  ON risks (asset_id);
CREATE INDEX IF NOT EXISTS idx_risks_score  ON risks (tenant_id, risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_risks_open   ON risks (tenant_id, treatment_status)
    WHERE treatment_status != 'implemented';

-- -----------------------------------------------------------------------------
-- vendors: third-party / processor register
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vendors (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(id),
    name                    TEXT NOT NULL,
    service_provided        TEXT,
    vendor_category         TEXT,
    data_subject_categories TEXT[],
    data_shared             TEXT,
    data_location           TEXT,
    dpa_signed              BOOLEAN,
    dpa_date                DATE,
    dpa_reference           TEXT,
    risk_level              TEXT
        CHECK (risk_level IN ('High','Medium','Low') OR risk_level IS NULL),
    security_controls       TEXT,
    compliance_certs        TEXT[],
    last_review_date        DATE,
    next_review_date        DATE,
    notes                   TEXT,
    is_processor            BOOLEAN NOT NULL DEFAULT FALSE,
    workbook_imported       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

CREATE INDEX IF NOT EXISTS idx_vendors_tenant    ON vendors (tenant_id);
CREATE INDEX IF NOT EXISTS idx_vendors_processor ON vendors (tenant_id, is_processor)
    WHERE is_processor = TRUE;

-- -----------------------------------------------------------------------------
-- isms_audits: audit programme records (internal + external)
-- Separate from audit_log which is a system event log
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS isms_audits (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id          UUID NOT NULL REFERENCES tenants(id),
    external_ref       TEXT,
    audit_type         TEXT NOT NULL DEFAULT 'internal'
        CHECK (audit_type IN ('internal','external','surveillance','recertification')),
    audit_date         DATE,
    auditor_name       TEXT,
    auditor_org        TEXT,
    scope              TEXT,
    standard_id        TEXT NOT NULL DEFAULT 'ISO27001:2022',
    outcome            TEXT
        CHECK (outcome IN ('pass','pass_with_ofi','fail','pending') OR outcome IS NULL),
    certificate_issued BOOLEAN NOT NULL DEFAULT FALSE,
    certificate_ref    TEXT,
    certificate_expiry DATE,
    finding_refs       TEXT[],
    report_document_id UUID REFERENCES client_documents(id),
    notes              TEXT,
    workbook_imported  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, external_ref)
);

CREATE INDEX IF NOT EXISTS idx_isms_audits_tenant ON isms_audits (tenant_id);
CREATE INDEX IF NOT EXISTS idx_isms_audits_date   ON isms_audits (tenant_id, audit_date DESC);

-- =============================================================================
-- SECTION 2: ADD MISSING COLUMNS TO EXISTING TABLES
-- (risks table now exists so FK is safe)
-- =============================================================================

-- posture_controls: external ref + workbook traceability
ALTER TABLE posture_controls
    ADD COLUMN IF NOT EXISTS external_ref         TEXT,
    ADD COLUMN IF NOT EXISTS soa_notes            TEXT,
    ADD COLUMN IF NOT EXISTS soa_justification    TEXT,
    ADD COLUMN IF NOT EXISTS linked_policies      TEXT[],
    ADD COLUMN IF NOT EXISTS owner_text           TEXT,
    ADD COLUMN IF NOT EXISTS workbook_imported    BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS workbook_import_date TIMESTAMPTZ;

-- client_documents: external ref + approval status + metadata-only flag
ALTER TABLE client_documents
    ADD COLUMN IF NOT EXISTS external_ref      TEXT,
    ADD COLUMN IF NOT EXISTS approval_status   TEXT
        CHECK (approval_status IN ('Approved','Pending','Draft','Superseded')
               OR approval_status IS NULL),
    ADD COLUMN IF NOT EXISTS is_metadata_only  BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS workbook_imported BOOLEAN NOT NULL DEFAULT FALSE;

-- Make storage_path nullable — documents can be registered before upload
ALTER TABLE client_documents
    ALTER COLUMN storage_path DROP NOT NULL;

-- incidents: external ref + workbook fields
ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS external_ref             TEXT,
    ADD COLUMN IF NOT EXISTS asset_ref                TEXT,
    ADD COLUMN IF NOT EXISTS pii_involved             BOOLEAN,
    ADD COLUMN IF NOT EXISTS authority_notified       BOOLEAN,
    ADD COLUMN IF NOT EXISTS data_subjects_notified   BOOLEAN,
    ADD COLUMN IF NOT EXISTS lessons_learned          TEXT,
    ADD COLUMN IF NOT EXISTS pii_restoration_auth_by TEXT,
    ADD COLUMN IF NOT EXISTS actions_taken            TEXT,
    ADD COLUMN IF NOT EXISTS evidence_collected       BOOLEAN,
    ADD COLUMN IF NOT EXISTS workbook_imported        BOOLEAN NOT NULL DEFAULT FALSE;

-- remediation_plans: risk FK + treatment fields (risks table now exists)
ALTER TABLE remediation_plans
    ADD COLUMN IF NOT EXISTS risk_id             UUID REFERENCES risks(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS risk_ref            TEXT,
    ADD COLUMN IF NOT EXISTS residual_risk       TEXT,
    ADD COLUMN IF NOT EXISTS residual_risk_level INT,
    ADD COLUMN IF NOT EXISTS treatment_option    TEXT,
    ADD COLUMN IF NOT EXISTS review_date         DATE,
    ADD COLUMN IF NOT EXISTS effectiveness_review TEXT,
    ADD COLUMN IF NOT EXISTS workbook_imported   BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- SECTION 3: INDEXES ON NEW COLUMNS
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_posture_external_ref
    ON posture_controls (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_documents_external_ref
    ON client_documents (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_documents_metadata_only
    ON client_documents (tenant_id, is_metadata_only)
    WHERE is_metadata_only = TRUE;

CREATE INDEX IF NOT EXISTS idx_incidents_external_ref
    ON incidents (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

-- =============================================================================
-- SECTION 4: CLIENT FACTS CORRECTIONS FOR ARION NETWORKS
-- Based on workbook evidence: SoA + vendor register
-- =============================================================================
UPDATE client_facts SET
    develops_software     = FALSE,   -- SoA: 8.25-8.31 all N/A "we don't do SW"
    has_physical_premises = FALSE,   -- SoA: 7.x all N/A "no physical assets exist"
    uses_cloud_services   = TRUE,    -- Azure, M365, Odoo, SharePoint
    uses_processors       = TRUE,    -- Microsoft, Odoo, Xeltec all confirmed processors
    has_remote_workers    = TRUE,    -- Remote Work and Device Security Policy exists
    collected_via         = 'workbook',
    last_updated          = NOW()
WHERE tenant_id = '00000000-0000-0000-0000-000000000001';


-- =============================================================================
-- SECTION 5: PLATFORM REFERENCE SCHEME
-- Human-readable, stable, cross-client consistent references
-- Format: {PREFIX}-{TENANT_SHORT}-{SEQUENCE}
-- =============================================================================

-- Reference prefixes registry
CREATE TABLE IF NOT EXISTS ref_prefixes (
    prefix          TEXT PRIMARY KEY,               -- CD, INC, AST etc
    entity_type     TEXT NOT NULL,                  -- client_documents, incidents etc
    table_name      TEXT NOT NULL,
    description     TEXT
);

INSERT INTO ref_prefixes (prefix, entity_type, table_name, description) VALUES
    ('PC',  'posture_control',   'posture_controls',   'Posture Control'),
    ('CD',  'document',          'client_documents',   'Client Document'),
    ('INC', 'incident',          'incidents',          'Incident'),
    ('AST', 'asset',             'assets',             'Asset'),
    ('RSK', 'risk',              'risks',              'Risk'),
    ('VND', 'vendor',            'vendors',            'Vendor / Supplier'),
    ('AUD', 'audit',             'isms_audits',        'ISMS Audit'),
    ('FND', 'finding',           'document_findings',  'Document Finding')
ON CONFLICT (prefix) DO NOTHING;

-- Sequence counters per tenant per prefix
CREATE TABLE IF NOT EXISTS ref_sequences (
    tenant_id   UUID    NOT NULL REFERENCES tenants(id),
    prefix      TEXT    NOT NULL REFERENCES ref_prefixes(prefix),
    next_seq    INT     NOT NULL DEFAULT 1,
    PRIMARY KEY (tenant_id, prefix)
);

-- Platform ref column added to each entity table
ALTER TABLE posture_controls  ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE client_documents  ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE incidents         ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE assets            ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE risks             ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE vendors           ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE isms_audits       ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;
ALTER TABLE document_findings ADD COLUMN IF NOT EXISTS platform_ref TEXT UNIQUE;

-- Function: generate next platform ref
-- Usage: SELECT next_platform_ref('00000000-...', 'CD', 'ARN')
CREATE OR REPLACE FUNCTION next_platform_ref(
    p_tenant_id   UUID,
    p_prefix      TEXT,
    p_tenant_short TEXT      -- 3-letter tenant abbreviation e.g. 'ARN'
) RETURNS TEXT AS $$
DECLARE
    v_seq INT;
    v_pad INT := CASE WHEN p_prefix IN ('INC', 'AUD') THEN 3 ELSE 4 END;
BEGIN
    INSERT INTO ref_sequences (tenant_id, prefix, next_seq)
    VALUES (p_tenant_id, p_prefix, 2)
    ON CONFLICT (tenant_id, prefix)
    DO UPDATE SET next_seq = ref_sequences.next_seq + 1
    RETURNING next_seq - 1 INTO v_seq;

    RETURN p_prefix || '-' || p_tenant_short || '-'
           || LPAD(v_seq::TEXT, v_pad, '0');
END;
$$ LANGUAGE plpgsql;

-- Tenant short codes
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS short_code TEXT;
UPDATE tenants SET short_code = 'ARN'
WHERE id = '00000000-0000-0000-0000-000000000001';

-- Unique constraint on short_code once data is clean
CREATE UNIQUE INDEX IF NOT EXISTS idx_tenants_short_code
    ON tenants (short_code) WHERE short_code IS NOT NULL;


-- =============================================================================
-- SECTION 6: GRANTS FOR APP USER
-- Run after every schema change — idempotent
-- =============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON assets        TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON risks         TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON vendors       TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON isms_audits   TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ref_prefixes  TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ref_sequences TO arioncomply_app;
GRANT EXECUTE ON FUNCTION next_platform_ref(UUID, TEXT, TEXT) TO arioncomply_app;

-- =============================================================================
-- SECTION 7: CONSTRAINT FIXES (revealed by workbook import run)
-- =============================================================================

-- Add 'workbook' to posture_controls source CHECK
-- The workbook importer is a legitimate source type
ALTER TABLE posture_controls DROP CONSTRAINT IF EXISTS posture_controls_source_check;
ALTER TABLE posture_controls ADD CONSTRAINT posture_controls_source_check
    CHECK (source IN ('chat','questionnaire','document','assessor',
                      'self_reported','workbook','Not assessed'));

-- Add unique indexes needed for UPSERT ON CONFLICT
-- posture_controls: NC tracker rows use external_ref as the conflict key
CREATE UNIQUE INDEX IF NOT EXISTS idx_posture_controls_tenant_external_ref
    ON posture_controls (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

-- client_documents: DOC001-DOC041 use external_ref
CREATE UNIQUE INDEX IF NOT EXISTS idx_client_documents_tenant_external_ref
    ON client_documents (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

-- incidents: INC002-INC003 use external_ref
CREATE UNIQUE INDEX IF NOT EXISTS idx_incidents_tenant_external_ref
    ON incidents (tenant_id, external_ref)
    WHERE external_ref IS NOT NULL;

-- vendors: name is the natural key
-- UNIQUE(tenant_id, name) already in CREATE TABLE — no change needed

-- Fix vendors risk_level CHECK to accept any case/format
-- Mapper now normalises to High/Medium/Low before insert, so CHECK is correct.
-- No schema change needed — the issue was in the mapper (now fixed).

-- Re-grant after constraint changes
GRANT SELECT, INSERT, UPDATE, DELETE ON assets        TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON risks         TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON vendors       TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON isms_audits   TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ref_prefixes  TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ref_sequences TO arioncomply_app;
GRANT EXECUTE ON FUNCTION next_platform_ref(UUID, TEXT, TEXT) TO arioncomply_app;


-- =============================================================================
-- SECTION 8: FULL UNIQUE INDEXES FOR ON CONFLICT
-- Partial indexes (WHERE x IS NOT NULL) are not recognised by Postgres
-- for ON CONFLICT clauses. Replace with full unique indexes.
-- =============================================================================

-- Drop the partial indexes added in Section 7
DROP INDEX IF EXISTS idx_posture_controls_tenant_external_ref;
DROP INDEX IF EXISTS idx_client_documents_tenant_external_ref;
DROP INDEX IF EXISTS idx_incidents_tenant_external_ref;

-- Create full unique indexes instead
-- NULL values are distinct in Postgres unique indexes — multiple NULL rows allowed
CREATE UNIQUE INDEX IF NOT EXISTS uidx_posture_controls_external_ref
    ON posture_controls (tenant_id, external_ref);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_client_documents_external_ref
    ON client_documents (tenant_id, external_ref);

CREATE UNIQUE INDEX IF NOT EXISTS uidx_incidents_external_ref
    ON incidents (tenant_id, external_ref);


-- =============================================================================
-- SECTION 9: ALLOW NULL control_ref FOR UNRESOLVED NC/OFI FINDINGS
-- NC tracker rows are findings not yet mapped to specific controls.
-- They are valid posture records with external_ref (F001-F007) but no
-- control_ref until a human or LLM maps them to the right control.
-- node_id also becomes nullable for the same reason.
-- =============================================================================
ALTER TABLE posture_controls
    ALTER COLUMN control_ref DROP NOT NULL,
    ALTER COLUMN node_id     DROP NOT NULL;

-- Partial unique index: when control_ref IS set, enforce tenant+standard+control uniqueness
-- When control_ref IS NULL (NC tracker rows), use external_ref uniqueness (already covered)
DROP INDEX IF EXISTS posture_controls_tenant_id_standard_id_control_ref_key;

CREATE UNIQUE INDEX IF NOT EXISTS uidx_posture_controls_control_ref
    ON posture_controls (tenant_id, standard_id, control_ref)
    WHERE control_ref IS NOT NULL;


-- =============================================================================
-- SECTION 10: SOURCE AUTHORITY — WHO ESTABLISHED THE FINDING
-- source:           HOW (chat / questionnaire / document / assessor / workbook)
-- source_authority: WHO (URS Certification, Arion Networks Internal Audit, etc.)
-- =============================================================================

ALTER TABLE posture_controls
    ADD COLUMN IF NOT EXISTS source_authority TEXT;  -- named entity who raised the finding

ALTER TABLE posture_history
    ADD COLUMN IF NOT EXISTS source_authority TEXT;

-- Populate source_authority from existing data
-- External audit findings (F004-F007): URS Certification s.r.o. (auditor Martin Kubiš)
UPDATE posture_controls SET source_authority = 'URS Certification s.r.o.'
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND soa_notes LIKE 'URS%';

-- Internal audit findings (F001, F002): Arion Networks Internal Audit
UPDATE posture_controls SET source_authority = 'Arion Networks Internal Audit'
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND soa_notes LIKE 'AUD001%';

-- Workbook self-assessment: Arion Networks (SoA v1.0)
UPDATE posture_controls SET source_authority = 'Arion Networks (SoA v1.0, 11.04.2025)'
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND source = 'workbook'
  AND source_authority IS NULL;


-- =============================================================================
-- SECTION 11: MAP NC TRACKER FINDINGS TO CONTROL REFS
-- The 7 workbook NC tracker rows (F001-F007) were imported without control_ref
-- because the NC tracker doesn't record control mappings explicitly.
-- We now map them based on audit evidence.
-- F001+F002 map to controls already covered by migrate_posture.py inserts —
-- these rows become redundant and should be merged or deleted.
-- =============================================================================

-- F003: Document register timestamps missing → A.5.9 (Information classification)
-- Actually maps to document management — A.5.9 covers information labelling
-- Better fit: not a control gap, it's a records management issue → A.5.9
UPDATE posture_controls SET
    control_ref      = 'A.5.9',
    node_id          = 'ISO27001:2022:A.5.9',
    source_authority = 'Arion Networks Internal Audit (AUD001, April 2025)'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F003'
  AND control_ref IS NULL;

-- F004: Business partners not assessed → A.5.19 (already covered by migrate_posture)
-- This row duplicates the PC-ARN-0104 row — mark it for review
UPDATE posture_controls SET
    control_ref      = 'A.5.19',
    node_id          = 'ISO27001:2022:A.5.19',
    source_authority = 'URS Certification s.r.o. (auditor: Martin Kubiš)',
    soa_notes        = 'URS 2025/214427/OA1 OFI #1 — duplicate of PC-ARN-0104'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F004'
  AND control_ref IS NULL;

-- F005: No formal access rights review → A.5.18 (already covered by migrate_posture)
UPDATE posture_controls SET
    control_ref      = 'A.5.18',
    node_id          = 'ISO27001:2022:A.5.18',
    source_authority = 'URS Certification s.r.o. (auditor: Martin Kubiš)',
    soa_notes        = 'URS 2025/214427/OA1 OFI #2 — see also PC-ARN-0105 (NC)'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F005'
  AND control_ref IS NULL;

-- F006: No software allow/deny list → A.8.19 (already covered by migrate_posture)
UPDATE posture_controls SET
    control_ref      = 'A.8.19',
    node_id          = 'ISO27001:2022:A.8.19',
    source_authority = 'URS Certification s.r.o. (auditor: Martin Kubiš)',
    soa_notes        = 'URS 2025/214427/OA1 OFI #3 — duplicate of PC-ARN-0106'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F006'
  AND control_ref IS NULL;

-- F007: Audit reports missing control list → 9.2 (already covered by migrate_posture)
UPDATE posture_controls SET
    control_ref      = '9.2',
    node_id          = 'ISO27001:2022:9.2',
    source_authority = 'URS Certification s.r.o. (auditor: Martin Kubiš)',
    soa_notes        = 'URS 2025/214427/OA1 OFI #4 — duplicate of PC-ARN-0107'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F007'
  AND control_ref IS NULL;

-- F001: Access register incomplete → A.5.18 (covered by PC-ARN-0105 NC)
UPDATE posture_controls SET
    control_ref      = 'A.5.18',
    node_id          = 'ISO27001:2022:A.5.18',
    source_authority = 'Arion Networks Internal Audit (AUD001, April 2025)',
    soa_notes        = 'AUD001 — duplicate of PC-ARN-0105 (NC, access register Q4 2024)'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F001'
  AND control_ref IS NULL;

-- F002: IR drill not done → A.5.26 (covered by PC-ARN-0108 NC)
UPDATE posture_controls SET
    control_ref      = 'A.5.26',
    node_id          = 'ISO27001:2022:A.5.26',
    source_authority = 'Arion Networks Internal Audit (AUD001, April 2025)',
    soa_notes        = 'AUD001 — duplicate of PC-ARN-0108 (NC, IR drill Q1 2025)'
WHERE tenant_id    = '00000000-0000-0000-0000-000000000001'
  AND external_ref = 'F002'
  AND control_ref IS NULL;

