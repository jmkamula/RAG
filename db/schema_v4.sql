-- =============================================================================
-- ArionComply — Schema v4
-- Document-Control cross references and filename registration
-- =============================================================================

-- =============================================================================
-- SECTION 1: CONTROL-DOCUMENT CROSS REFERENCE TABLE
-- Explicit many-to-many between posture_controls and client_documents
-- Replaces the free-text linked_policies array
-- =============================================================================

CREATE TABLE IF NOT EXISTS control_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID    NOT NULL REFERENCES tenants(id),
    control_id      UUID    NOT NULL REFERENCES posture_controls(id),
    document_id     UUID    NOT NULL REFERENCES client_documents(id),
    relationship    TEXT    NOT NULL DEFAULT 'evidences'
        CHECK (relationship IN (
            'evidences',    -- document is evidence the control is implemented
            'defines',      -- document defines the policy for this control
            'requires',     -- control requires this document to exist
            'templates'     -- document is a template for this control
        )),
    source          TEXT    DEFAULT 'workbook',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, control_id, document_id, relationship)
);

CREATE INDEX IF NOT EXISTS idx_ctrl_docs_tenant   ON control_documents (tenant_id);
CREATE INDEX IF NOT EXISTS idx_ctrl_docs_control  ON control_documents (control_id);
CREATE INDEX IF NOT EXISTS idx_ctrl_docs_document ON control_documents (document_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON control_documents TO arioncomply_app;

-- =============================================================================
-- SECTION 2: POPULATE CONTROL-DOCUMENT CROSS REFERENCES
-- From the SoA linked_policies data
-- =============================================================================

-- Map: control_ref → document external_ref (from linked_policies analysis)
-- DOC003 = Privacy and Information Security and Data Management Policy
-- DOC006 = Access Control Policy
-- DOC008 = Confidentiality and NDA Policy
-- DOC011 = Supplier and Vendor Security Policy
-- DOC016 = Information Security and Data Management Process
-- DOC024 = Vendor Security Assessment Report

DO $$
DECLARE
    v_tenant UUID := '00000000-0000-0000-0000-000000000001';
    v_ctrl   UUID;
    v_doc    UUID;
    r        RECORD;
BEGIN
    -- Map of control_ref → document external_ref
    FOR r IN SELECT * FROM (VALUES
        ('5.1',  'DOC003'), ('5.2',  'DOC003'),
        ('5.10', 'DOC003'), ('5.12', 'DOC003'), ('5.13', 'DOC003'),
        ('5.14', 'DOC003'), ('5.16', 'DOC003'), ('5.23', 'DOC003'),
        ('5.25', 'DOC003'), ('5.26', 'DOC003'),
        ('5.15', 'DOC006'), ('5.18', 'DOC006'),
        ('5.11', 'DOC008'),
        ('5.19', 'DOC011'), ('5.20', 'DOC011'), ('5.22', 'DOC011'),
        ('5.17', 'DOC016'), ('5.24', 'DOC016'),
        ('5.21', 'DOC024')
    ) AS t(ctrl_ref, doc_ref)
    LOOP
        SELECT id INTO v_ctrl FROM posture_controls
        WHERE tenant_id = v_tenant AND control_ref = r.ctrl_ref
        LIMIT 1;

        SELECT id INTO v_doc FROM client_documents
        WHERE tenant_id = v_tenant AND external_ref = r.doc_ref
        LIMIT 1;

        IF v_ctrl IS NOT NULL AND v_doc IS NOT NULL THEN
            INSERT INTO control_documents
                (tenant_id, control_id, document_id, relationship, source)
            VALUES
                (v_tenant, v_ctrl, v_doc, 'evidences', 'workbook')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END $$;

-- =============================================================================
-- SECTION 3: ADD FILENAME TO CLIENT_DOCUMENTS
-- The workbook stores filenames like DOC001_Scope_of_the_ISMS_and_PIMS.pdf
-- Register these so the uploader can match files
-- =============================================================================

-- filename column already exists from schema_v2
-- Just update the filename values based on the pattern DOCxxx_<title>.pdf

UPDATE client_documents SET filename = CONCAT(
    external_ref, '_',
    REGEXP_REPLACE(
        REGEXP_REPLACE(document_title, '[^a-zA-Z0-9 ]', '', 'g'),
        ' ', '_', 'g'
    ), '.pdf'
)
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND filename IS NULL
  AND external_ref IS NOT NULL;

-- =============================================================================
-- SECTION 4: DOCUMENT PRIORITY VIEW
-- Which documents should be uploaded first based on gap findings
-- =============================================================================

CREATE OR REPLACE VIEW document_upload_priority AS
SELECT
    cd.platform_ref,
    cd.external_ref,
    cd.document_title,
    cd.filename,
    cd.storage_path IS NOT NULL         AS has_file,
    cd.is_metadata_only,
    -- Priority based on linked control findings
    MIN(CASE pc.finding
        WHEN 'NC'  THEN 1
        WHEN 'OFI' THEN 2
        WHEN 'Comply' THEN 3
        ELSE 4
    END)                                AS priority_score,
    STRING_AGG(DISTINCT pc.control_ref, ', ' ORDER BY pc.control_ref)
                                        AS linked_controls,
    STRING_AGG(DISTINCT pc.finding, ', ')
                                        AS linked_findings
FROM client_documents cd
LEFT JOIN control_documents ctd ON ctd.document_id = cd.id
LEFT JOIN posture_controls pc   ON pc.id = ctd.control_id
WHERE cd.tenant_id = '00000000-0000-0000-0000-000000000001'
GROUP BY cd.id, cd.platform_ref, cd.external_ref,
         cd.document_title, cd.filename, cd.storage_path, cd.is_metadata_only
ORDER BY priority_score NULLS LAST, cd.external_ref;

GRANT SELECT ON document_upload_priority TO arioncomply_app;


-- =============================================================================
-- SECTION 5: DOCUMENT STATUS LIFECYCLE
-- Tracks every document through its lifecycle with clear status codes
-- Customers and the platform can always see what's missing and why it matters
-- =============================================================================

-- Add document_status column with clear lifecycle states
ALTER TABLE client_documents
    ADD COLUMN IF NOT EXISTS document_status TEXT NOT NULL DEFAULT 'registered'
        CHECK (document_status IN (
            'registered',       -- metadata only, file not uploaded
            'uploaded',         -- file received, not yet processed
            'processing',       -- pipeline running (extract/evaluate)
            'active',           -- processed and queryable
            'superseded',       -- replaced by a newer version
            'withdrawn'         -- removed from scope
        ));

ALTER TABLE client_documents
    ADD COLUMN IF NOT EXISTS status_reason    TEXT,       -- why this status
    ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS review_due_at    TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS version          TEXT DEFAULT '1.0',
    ADD COLUMN IF NOT EXISTS owner_name       TEXT;       -- document owner

-- Back-fill: all current rows are 'registered' (metadata only, no file)
UPDATE client_documents
SET document_status = 'registered',
    status_reason   = 'Imported from workbook — file not yet uploaded'
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND storage_path IS NULL;

-- =============================================================================
-- SECTION 6: DOCUMENT ALERTS VIEW
-- The view a customer dashboard would query to show "action required"
-- Prioritised by the severity of the gaps the missing document covers
-- =============================================================================

CREATE OR REPLACE VIEW document_alerts AS
WITH doc_priority AS (
    SELECT
        cd.id,
        cd.tenant_id,
        cd.platform_ref,
        cd.external_ref,
        cd.document_title,
        cd.document_type,
        cd.document_status,
        cd.filename,
        cd.approval_status,
        cd.version,
        cd.owner_name,
        cd.last_reviewed_at,
        cd.review_due_at,
        -- Worst finding linked to this document
        MIN(CASE pc.finding
            WHEN 'NC'     THEN 1
            WHEN 'OFI'    THEN 2
            WHEN 'Comply' THEN 3
            ELSE              4
        END)                                    AS worst_finding_score,
        STRING_AGG(DISTINCT pc.finding, ', ')   AS linked_findings,
        STRING_AGG(DISTINCT pc.control_ref, ', '
                   ORDER BY pc.control_ref)     AS linked_controls,
        COUNT(DISTINCT pc.id)                   AS control_count
    FROM client_documents cd
    LEFT JOIN control_documents ctd ON ctd.document_id = cd.id
    LEFT JOIN posture_controls  pc  ON pc.id = ctd.control_id
    GROUP BY cd.id, cd.tenant_id, cd.platform_ref, cd.external_ref,
             cd.document_title, cd.document_type, cd.document_status,
             cd.filename, cd.approval_status, cd.version, cd.owner_name,
             cd.last_reviewed_at, cd.review_due_at
)
SELECT
    platform_ref,
    external_ref,
    document_title,
    document_status,
    -- Alert type
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1
            THEN 'CRITICAL'     -- missing file, linked to NC
        WHEN document_status = 'registered' AND worst_finding_score = 2
            THEN 'WARNING'      -- missing file, linked to OFI
        WHEN document_status = 'registered' AND worst_finding_score <= 4
            THEN 'INFO'         -- missing file, linked to Comply controls
        WHEN document_status = 'registered'
            THEN 'INFO'         -- missing file, no findings yet
        WHEN review_due_at IS NOT NULL AND review_due_at < NOW()
            THEN 'WARNING'      -- file uploaded but review overdue
        ELSE NULL               -- no alert needed
    END                                         AS alert_type,
    -- Alert message
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1
            THEN 'File not uploaded — required evidence for open NC finding on '
                 || linked_controls
        WHEN document_status = 'registered' AND worst_finding_score = 2
            THEN 'File not uploaded — referenced by OFI finding on '
                 || linked_controls
        WHEN document_status = 'registered'
            THEN 'File not uploaded — registered as metadata only'
        WHEN review_due_at IS NOT NULL AND review_due_at < NOW()
            THEN 'Document review overdue since '
                 || TO_CHAR(review_due_at, 'YYYY-MM-DD')
        ELSE 'No action required'
    END                                         AS alert_message,
    linked_controls,
    linked_findings,
    control_count,
    worst_finding_score,
    filename,
    version,
    owner_name,
    approval_status,
    last_reviewed_at,
    review_due_at,
    tenant_id
FROM doc_priority
WHERE
    document_status = 'registered'              -- missing file
    OR (review_due_at IS NOT NULL
        AND review_due_at < NOW())              -- overdue review
ORDER BY
    worst_finding_score NULLS LAST,            -- NC first
    document_title;

GRANT SELECT ON document_alerts TO arioncomply_app;

-- =============================================================================
-- SECTION 7: TRIGGER — AUTO-UPDATE document_status ON FILE UPLOAD
-- When storage_path is set, automatically transition status to 'uploaded'
-- Pipeline then moves it to 'processing' → 'active'
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_update_document_status()
RETURNS TRIGGER AS $$
BEGIN
    -- File just added (storage_path was NULL, now set)
    IF OLD.storage_path IS NULL AND NEW.storage_path IS NOT NULL THEN
        NEW.document_status  := 'uploaded';
        NEW.is_metadata_only := FALSE;
        NEW.status_reason    := 'File uploaded at ' ||
                                TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI');
    END IF;
    -- File removed (shouldn't happen but handle gracefully)
    IF OLD.storage_path IS NOT NULL AND NEW.storage_path IS NULL THEN
        NEW.document_status  := 'registered';
        NEW.is_metadata_only := TRUE;
        NEW.status_reason    := 'File removed at ' ||
                                TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI');
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_document_status ON client_documents;
CREATE TRIGGER trg_document_status
    BEFORE UPDATE OF storage_path ON client_documents
    FOR EACH ROW EXECUTE FUNCTION fn_update_document_status();


-- =============================================================================
-- SECTION 8: ROW LEVEL SECURITY + PROPERLY SCOPED VIEWS
-- Fixes the tenant isolation gap in document_alerts and document_upload_priority
--
-- Strategy:
--   1. RLS on control_documents (new table, needs it)
--   2. Drop and recreate views to accept tenant_id parameter
--   3. Application passes tenant_id explicitly — no hardcoding
-- =============================================================================

-- Enable RLS on control_documents (other tables already have it or will)
ALTER TABLE control_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY ctrl_docs_tenant_isolation ON control_documents
    USING (tenant_id = (
        NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID
    ));

-- Grant bypass to superuser only (not the app user)
-- App user always goes through RLS

-- ── Drop and rebuild document_upload_priority with proper tenant param ────────
DROP VIEW IF EXISTS document_upload_priority;

CREATE OR REPLACE VIEW document_upload_priority AS
SELECT
    cd.platform_ref,
    cd.external_ref,
    cd.document_title,
    cd.filename,
    cd.storage_path IS NOT NULL                     AS has_file,
    cd.is_metadata_only,
    cd.document_status,
    cd.tenant_id,
    MIN(CASE pc.finding
        WHEN 'NC'     THEN 1
        WHEN 'OFI'    THEN 2
        WHEN 'Comply' THEN 3
        ELSE              4
    END)                                            AS priority_score,
    STRING_AGG(DISTINCT pc.control_ref, ', '
               ORDER BY pc.control_ref)             AS linked_controls,
    STRING_AGG(DISTINCT pc.finding, ', ')           AS linked_findings
FROM client_documents cd
LEFT JOIN control_documents ctd ON ctd.document_id = cd.id
                                AND ctd.tenant_id   = cd.tenant_id
LEFT JOIN posture_controls  pc  ON pc.id            = ctd.control_id
                                AND pc.tenant_id    = cd.tenant_id
-- No WHERE clause — RLS on base tables enforces tenant isolation
GROUP BY cd.id, cd.platform_ref, cd.external_ref,
         cd.document_title, cd.filename, cd.storage_path,
         cd.is_metadata_only, cd.document_status, cd.tenant_id
ORDER BY priority_score NULLS LAST, cd.external_ref;

-- ── Drop and rebuild document_alerts with proper tenant isolation ─────────────
DROP VIEW IF EXISTS document_alerts;

CREATE OR REPLACE VIEW document_alerts AS
WITH doc_priority AS (
    SELECT
        cd.id,
        cd.tenant_id,
        cd.platform_ref,
        cd.external_ref,
        cd.document_title,
        cd.document_type,
        cd.document_status,
        cd.filename,
        cd.approval_status,
        cd.version,
        cd.owner_name,
        cd.last_reviewed_at,
        cd.review_due_at,
        MIN(CASE pc.finding
            WHEN 'NC'     THEN 1
            WHEN 'OFI'    THEN 2
            WHEN 'Comply' THEN 3
            ELSE              4
        END)                                        AS worst_finding_score,
        STRING_AGG(DISTINCT pc.finding, ', ')       AS linked_findings,
        STRING_AGG(DISTINCT pc.control_ref, ', '
                   ORDER BY pc.control_ref)         AS linked_controls,
        COUNT(DISTINCT pc.id)                       AS control_count
    FROM client_documents cd
    LEFT JOIN control_documents ctd ON ctd.document_id = cd.id
                                    AND ctd.tenant_id   = cd.tenant_id
    LEFT JOIN posture_controls  pc  ON pc.id            = ctd.control_id
                                    AND pc.tenant_id    = cd.tenant_id
    -- RLS on client_documents, control_documents, posture_controls
    -- enforces tenant isolation — no WHERE needed here
    GROUP BY cd.id, cd.tenant_id, cd.platform_ref, cd.external_ref,
             cd.document_title, cd.document_type, cd.document_status,
             cd.filename, cd.approval_status, cd.version, cd.owner_name,
             cd.last_reviewed_at, cd.review_due_at
)
SELECT
    platform_ref,
    external_ref,
    document_title,
    document_status,
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1
            THEN 'CRITICAL'
        WHEN document_status = 'registered' AND worst_finding_score = 2
            THEN 'WARNING'
        WHEN document_status = 'registered'
            THEN 'INFO'
        WHEN review_due_at IS NOT NULL AND review_due_at < NOW()
            THEN 'WARNING'
        ELSE NULL
    END                                             AS alert_type,
    CASE
        WHEN document_status = 'registered' AND worst_finding_score = 1
            THEN 'File not uploaded — required evidence for NC finding on '
                 || COALESCE(linked_controls, 'unknown control')
        WHEN document_status = 'registered' AND worst_finding_score = 2
            THEN 'File not uploaded — referenced by OFI finding on '
                 || COALESCE(linked_controls, 'unknown control')
        WHEN document_status = 'registered'
            THEN 'File not uploaded — registered as metadata only'
        WHEN review_due_at IS NOT NULL AND review_due_at < NOW()
            THEN 'Review overdue since ' || TO_CHAR(review_due_at, 'YYYY-MM-DD')
        ELSE 'No action required'
    END                                             AS alert_message,
    linked_controls,
    linked_findings,
    control_count,
    worst_finding_score,
    filename,
    version,
    owner_name,
    approval_status,
    last_reviewed_at,
    review_due_at,
    tenant_id                   -- exposed for app-layer filtering as backup
FROM doc_priority
WHERE document_status = 'registered'
   OR (review_due_at IS NOT NULL AND review_due_at < NOW())
ORDER BY worst_finding_score NULLS LAST, document_title;

GRANT SELECT ON document_upload_priority TO arioncomply_app;
GRANT SELECT ON document_alerts          TO arioncomply_app;


-- =============================================================================
-- SECTION 9: FIX CONTROL-DOCUMENT LINKS FOR NC/OFI FINDINGS
-- The SoA uses "5.18" format but NC/OFI findings use "A.5.18" format
-- Add cross-references for the Annex A format refs so alerts show CRITICAL/WARNING
-- =============================================================================

DO $$
DECLARE
    v_tenant UUID := '00000000-0000-0000-0000-000000000001';
    v_ctrl   UUID;
    v_doc    UUID;
    r        RECORD;
BEGIN
    -- Map Annex A control refs → documents (NC/OFI finding rows use A.x.xx format)
    FOR r IN SELECT * FROM (VALUES
        -- A.5.18 NC → Access Control Policy (DOC006) + Access Management Process (DOC013)
        ('A.5.18', 'DOC006'),
        ('A.5.18', 'DOC013'),
        -- A.5.19 OFI → Supplier and Vendor Security Policy (DOC011)
        ('A.5.19', 'DOC011'),
        ('A.5.19', 'DOC019'),  -- Supplier and Vendor Security Process
        -- A.5.26 NC → IR Playbook (DOC040) + Simulation Report Template (DOC041)
        ('A.5.26', 'DOC040'),
        ('A.5.26', 'DOC041'),
        -- A.8.19 OFI → Security Vulnerability Management (DOC029)
        ('A.8.19', 'DOC029'),
        -- 9.2 OFI → Internal Audit Policy (DOC035) + Internal Audit Plan (DOC020)
        ('9.2',    'DOC035'),
        ('9.2',    'DOC020'),
        ('9.2',    'DOC036'),  -- Internal Audit Report Template
        -- A.5.9 OFI → TOC Information Security Documents (DOC022)
        ('A.5.9',  'DOC022')
    ) AS t(ctrl_ref, doc_ref)
    LOOP
        SELECT id INTO v_ctrl FROM posture_controls
        WHERE tenant_id = v_tenant AND control_ref = r.ctrl_ref
        LIMIT 1;

        SELECT id INTO v_doc FROM client_documents
        WHERE tenant_id = v_tenant AND external_ref = r.doc_ref
        LIMIT 1;

        IF v_ctrl IS NOT NULL AND v_doc IS NOT NULL THEN
            INSERT INTO control_documents
                (tenant_id, control_id, document_id, relationship, source)
            VALUES
                (v_tenant, v_ctrl, v_doc, 'evidences', 'workbook')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END $$;

