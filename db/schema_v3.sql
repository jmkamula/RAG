-- =============================================================================
-- ArionComply — Schema v3
-- Standards Registry + Tenant Enrollment + Automatic Scope Inference
-- =============================================================================

-- =============================================================================
-- SECTION 1: STANDARDS REGISTRY
-- Every standard the platform knows about, with relationships
-- =============================================================================

CREATE TABLE IF NOT EXISTS standards (
    id              TEXT PRIMARY KEY,           -- "ISO27001:2022"
    family          TEXT NOT NULL,              -- "ISO27001", "ISO27701", "GDPR"
    version         TEXT NOT NULL,              -- "2022", "2019", "2016/679"
    full_name       TEXT NOT NULL,              -- "ISO/IEC 27001:2022"
    short_name      TEXT NOT NULL,              -- "ISO 27001"
    standard_type   TEXT NOT NULL               -- "management_system" | "regulation" | "framework"
        CHECK (standard_type IN (
            'management_system',  -- ISO 27001, ISO 27701 — certifiable
            'regulation',         -- GDPR — legal obligation, not certifiable
            'framework',          -- NIST CSF, CIS Controls — advisory
            'code_of_practice'    -- ISO 27002 — guidance only
        )),
    certifiable     BOOLEAN NOT NULL DEFAULT FALSE,
    jurisdiction    TEXT,                       -- "EU", "US", "global"
    description     TEXT,
    annex_mapping   TEXT,                       -- "Annex D" — where mapping table is
    loaded_in_graph BOOLEAN NOT NULL DEFAULT FALSE,  -- nodes in Neo4j/ChromaDB?
    node_count      INT,                        -- how many RequirementNodes loaded
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Standard relationships
CREATE TABLE IF NOT EXISTS standard_relationships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       TEXT NOT NULL REFERENCES standards(id),
    target_id       TEXT NOT NULL REFERENCES standards(id),
    relationship    TEXT NOT NULL
        CHECK (relationship IN (
            'extends',      -- ISO 27701 extends ISO 27001
            'maps_to',      -- ISO 27701 maps_to GDPR (via Annex D)
            'requires',     -- implementing X requires Y
            'satisfies',    -- implementing X satisfies Y obligations
            'references'    -- X references Y (informative)
        )),
    mapping_source  TEXT,                       -- "ISO27701:2019 Annex D"
    coverage        TEXT                        -- "full" | "partial"
        CHECK (coverage IN ('full', 'partial') OR coverage IS NULL),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_id, target_id, relationship)
);

-- =============================================================================
-- SECTION 2: TENANT STANDARD ENROLLMENTS
-- Which standards each tenant has implemented / is implementing
-- =============================================================================

CREATE TABLE IF NOT EXISTS tenant_standards (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    standard_id         TEXT NOT NULL REFERENCES standards(id),
    status              TEXT NOT NULL DEFAULT 'implementing'
        CHECK (status IN (
            'implementing',   -- in progress
            'implemented',    -- self-assessed complete
            'certified',      -- third-party certified
            'surveillance',   -- maintaining certification
            'lapsed'          -- was certified, now lapsed
        )),
    -- Certification details
    cert_body           TEXT,                   -- "URS Certification s.r.o."
    cert_ref            TEXT,                   -- "2025/214427/OA1"
    cert_date           DATE,                   -- date cert was granted
    cert_expiry         DATE,                   -- expiry date
    next_audit_date     DATE,
    -- Scope
    soa_version         TEXT,                   -- "1.0"
    soa_date            DATE,                   -- "2025-04-11"
    scope_description   TEXT,
    -- Metadata
    enrolled_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, standard_id)
);

CREATE INDEX IF NOT EXISTS idx_tenant_standards_tenant
    ON tenant_standards (tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_standards_status
    ON tenant_standards (tenant_id, status);

-- =============================================================================
-- SECTION 3: SCOPE INFERENCE VIEW
-- Automatically derives what a tenant can be evaluated against
-- based on their enrollments + standard relationships
-- =============================================================================

CREATE OR REPLACE VIEW tenant_evaluation_scope AS
WITH
-- Direct standards the tenant implements
direct AS (
    SELECT
        ts.tenant_id,
        ts.standard_id,
        ts.status,
        s.standard_type,
        s.certifiable,
        'direct'        AS scope_source,
        ts.standard_id  AS via_standard,
        NULL::TEXT      AS relationship
    FROM tenant_standards ts
    JOIN standards s ON s.id = ts.standard_id
    WHERE ts.status IN ('implementing','implemented','certified','surveillance')
),
-- Standards reachable via relationships (e.g. GDPR via ISO 27701 maps_to)
inferred AS (
    SELECT
        d.tenant_id,
        sr.target_id        AS standard_id,
        d.status,
        s.standard_type,
        s.certifiable,
        'inferred'          AS scope_source,
        d.standard_id       AS via_standard,
        sr.relationship     AS relationship
    FROM direct d
    JOIN standard_relationships sr ON sr.source_id = d.standard_id
    JOIN standards s ON s.id = sr.target_id
    WHERE sr.relationship IN ('maps_to', 'satisfies')
)
SELECT * FROM direct
UNION ALL
SELECT * FROM inferred;

-- =============================================================================
-- SECTION 4: SEED DATA — KNOWN STANDARDS AND RELATIONSHIPS
-- =============================================================================

INSERT INTO standards (id, family, version, full_name, short_name,
    standard_type, certifiable, jurisdiction, description,
    annex_mapping, loaded_in_graph) VALUES

('ISO27001:2022', 'ISO27001', '2022',
 'ISO/IEC 27001:2022', 'ISO 27001',
 'management_system', TRUE, 'global',
 'Information Security Management Systems — Requirements',
 NULL, TRUE),

('ISO27002:2022', 'ISO27002', '2022',
 'ISO/IEC 27002:2022', 'ISO 27002',
 'code_of_practice', FALSE, 'global',
 'Information Security Controls — guidance for ISO 27001 Annex A',
 NULL, TRUE),

('ISO27701:2019', 'ISO27701', '2019',
 'ISO/IEC 27701:2019', 'ISO 27701',
 'management_system', TRUE, 'global',
 'Privacy Information Management System — Extension to ISO 27001/27002',
 'Annex D', FALSE),  -- not yet loaded in graph

('GDPR:2016/679', 'GDPR', '2016/679',
 'General Data Protection Regulation (EU) 2016/679', 'GDPR',
 'regulation', FALSE, 'EU',
 'EU regulation on protection of natural persons with regard to processing of personal data',
 NULL, TRUE),

('ISO27018:2019', 'ISO27018', '2019',
 'ISO/IEC 27018:2019', 'ISO 27018',
 'code_of_practice', FALSE, 'global',
 'Protection of PII in public clouds — extends ISO 27001/27701',
 NULL, FALSE),

('NIST-CSF:2.0', 'NIST-CSF', '2.0',
 'NIST Cybersecurity Framework 2.0', 'NIST CSF',
 'framework', FALSE, 'US',
 'Framework for improving critical infrastructure cybersecurity',
 NULL, FALSE)

ON CONFLICT (id) DO NOTHING;


-- Standard relationships
INSERT INTO standard_relationships
    (source_id, target_id, relationship, mapping_source, coverage, notes)
VALUES

-- ISO 27701 extends ISO 27001 (it's a PIMS extension)
('ISO27701:2019', 'ISO27001:2022', 'extends',
 'ISO 27701:2019 Introduction', 'full',
 'ISO 27701 adds PIMS requirements to ISO 27001 ISMS'),

-- ISO 27701 maps to GDPR (Annex D provides explicit mapping)
('ISO27701:2019', 'GDPR:2016/679', 'maps_to',
 'ISO 27701:2019 Annex D', 'partial',
 'Annex D maps ISO 27701 controls to GDPR articles. Coverage is partial — not every GDPR article has a direct 27701 control.'),

-- ISO 27701 satisfies GDPR obligations (implementing 27701 demonstrates GDPR compliance)
('ISO27701:2019', 'GDPR:2016/679', 'satisfies',
 'ISO 27701:2019 Introduction', 'partial',
 'ISO 27701 certification provides evidence of GDPR compliance measures but does not guarantee full legal compliance'),

-- ISO 27001 references ISO 27002 (Annex A controls defined in 27002)
('ISO27001:2022', 'ISO27002:2022', 'references',
 'ISO 27001:2022 Annex A', 'full',
 'ISO 27001 Annex A controls are defined in ISO 27002'),

-- ISO 27701 references ISO 27018 (cloud PII guidance)
('ISO27701:2019', 'ISO27018:2019', 'references',
 'ISO 27701:2019', 'partial',
 'ISO 27018 provides additional guidance for cloud PII processing')

ON CONFLICT (source_id, target_id, relationship) DO NOTHING;


-- =============================================================================
-- SECTION 5: ENROLL ARION NETWORKS
-- =============================================================================

-- Enroll Arion in ISO 27001 (certified April 2025)
INSERT INTO tenant_standards (
    tenant_id, standard_id, status,
    cert_body, cert_ref, cert_date,
    soa_version, soa_date, scope_description
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'ISO27001:2022',
    'certified',
    'URS Certification s.r.o.',
    '2025/214427/OA1',
    '2025-05-07',
    '1.0',
    '2025-04-11',
    'Information Security Management Related to Technical Consulting and Training Services'
)
ON CONFLICT (tenant_id, standard_id) DO UPDATE SET
    status   = EXCLUDED.status,
    cert_body = EXCLUDED.cert_body,
    cert_ref  = EXCLUDED.cert_ref,
    cert_date = EXCLUDED.cert_date;

-- Enroll Arion in ISO 27701 (implementing — not yet certified)
INSERT INTO tenant_standards (
    tenant_id, standard_id, status,
    soa_version, soa_date, scope_description
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'ISO27701:2019',
    'implementing',
    '1.0',
    '2025-04-11',
    'Privacy Information Management related to Technical Consulting and Training Services'
)
ON CONFLICT (tenant_id, standard_id) DO NOTHING;

-- =============================================================================
-- SECTION 6: GRANTS
-- =============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON standards              TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON standard_relationships TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_standards       TO arioncomply_app;
GRANT SELECT ON tenant_evaluation_scope                        TO arioncomply_app;

