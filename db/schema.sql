-- =============================================================================
-- ArionComply — Compliance Database Schema
-- =============================================================================
-- Database:     arioncomply_compliance
-- Tenancy:      Shared schema, tenant_id on every row, RLS enforced
-- Retention:    Mechanism 2 — scheduled purge via retention_policies table
-- Storage:      Option B — S3/filesystem for files, Postgres for metadata
--               full_text is nullable — NULL when text lives in S3
--
-- Apply:
--   psql arioncomply_compliance -f db/schema.sql
-- =============================================================================

-- ── Extensions ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
-- pg_cron: installed separately in production, skipped for local dev
-- pgvector: enable when document embeddings are needed


-- =============================================================================
-- ORGANISATION DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    sector          TEXT,
    country         TEXT DEFAULT 'GB',
    timezone        TEXT DEFAULT 'Europe/London',
    subscription    TEXT NOT NULL DEFAULT 'free'
        CHECK (subscription IN ('free','starter','professional','enterprise')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS roles (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    description         TEXT NOT NULL,
    can_write_posture   BOOLEAN NOT NULL DEFAULT FALSE,
    can_write_incidents BOOLEAN NOT NULL DEFAULT FALSE,
    can_write_documents BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_users    BOOLEAN NOT NULL DEFAULT FALSE,
    can_view_all        BOOLEAN NOT NULL DEFAULT FALSE,
    is_arion_staff      BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO roles (name, description,
    can_write_posture, can_write_incidents, can_write_documents,
    can_manage_users, can_view_all, is_arion_staff)
VALUES
('admin',              'Tenant administrator — full access, manages users',
    TRUE, TRUE, TRUE, TRUE, TRUE, FALSE),
('compliance_manager', 'Owns the ISMS — manages posture, documents, incidents',
    TRUE, TRUE, TRUE, FALSE, TRUE, FALSE),
('dpo',                'Data Protection Officer — full GDPR scope, breach authority',
    TRUE, TRUE, TRUE, FALSE, TRUE, FALSE),
('ciso',               'CISO — reads all, writes technical controls only',
    TRUE, FALSE, TRUE, FALSE, TRUE, FALSE),
('staff',              'Can submit evidence and view own area only',
    FALSE, FALSE, TRUE, FALSE, FALSE, FALSE),
('arion_advisor',      'ArionComply support — reads all, annotates, cannot alter posture',
    FALSE, FALSE, FALSE, FALSE, TRUE, TRUE),
('auditor',            'External auditor — time-limited read-only access',
    FALSE, FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_tenant ON users (tenant_id);

CREATE TABLE IF NOT EXISTS user_roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    role_id     INT  NOT NULL REFERENCES roles(id),
    granted_by  UUID REFERENCES users(id),
    granted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    revoked_at  TIMESTAMPTZ,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user   ON user_roles (user_id)   WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_user_roles_tenant ON user_roles (tenant_id) WHERE is_active;

CREATE TABLE IF NOT EXISTS applicable_standards (
    tenant_id       UUID NOT NULL REFERENCES tenants(id),
    standard_id     TEXT NOT NULL,
    in_scope        BOOLEAN NOT NULL DEFAULT TRUE,
    added_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, standard_id)
);

CREATE TABLE IF NOT EXISTS client_facts (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                   UUID NOT NULL REFERENCES tenants(id) UNIQUE,
    processes_personal_data     BOOLEAN NOT NULL DEFAULT FALSE,
    eu_data_subjects            BOOLEAN NOT NULL DEFAULT FALSE,
    uk_data_subjects            BOOLEAN NOT NULL DEFAULT FALSE,
    role_controller             BOOLEAN NOT NULL DEFAULT FALSE,
    role_processor              BOOLEAN NOT NULL DEFAULT FALSE,
    role_joint_controller       BOOLEAN NOT NULL DEFAULT FALSE,
    special_category_data       BOOLEAN NOT NULL DEFAULT FALSE,
    criminal_conviction_data    BOOLEAN NOT NULL DEFAULT FALSE,
    childrens_data              BOOLEAN NOT NULL DEFAULT FALSE,
    automated_decision_making   BOOLEAN NOT NULL DEFAULT FALSE,
    profiling                   BOOLEAN NOT NULL DEFAULT FALSE,
    large_scale_processing      BOOLEAN NOT NULL DEFAULT FALSE,
    systematic_monitoring       BOOLEAN NOT NULL DEFAULT FALSE,
    high_risk_processing        BOOLEAN NOT NULL DEFAULT FALSE,
    employee_count_250_plus     BOOLEAN NOT NULL DEFAULT FALSE,
    public_authority            BOOLEAN NOT NULL DEFAULT FALSE,
    sector                      TEXT,
    uses_processors             BOOLEAN NOT NULL DEFAULT FALSE,
    uses_cloud_services         BOOLEAN NOT NULL DEFAULT FALSE,
    transfers_data_outside_eu   BOOLEAN NOT NULL DEFAULT FALSE,
    develops_software           BOOLEAN NOT NULL DEFAULT FALSE,
    has_remote_workers          BOOLEAN NOT NULL DEFAULT FALSE,
    has_physical_premises       BOOLEAN NOT NULL DEFAULT TRUE,
    collected_via               TEXT DEFAULT 'questionnaire',
    last_updated                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by                  UUID REFERENCES users(id)
);


-- =============================================================================
-- POSTURE DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS posture_controls (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    standard_id         TEXT NOT NULL,
    control_ref         TEXT NOT NULL,
    node_id             TEXT NOT NULL,

    finding             TEXT NOT NULL DEFAULT 'Not assessed'
        CHECK (finding IN ('NC','OFI','Comply','N/A','Not assessed')),
    confidence          TEXT NOT NULL DEFAULT 'medium'
        CHECK (confidence IN ('high','medium','low')),
    gap_description     TEXT,
    action_required     TEXT,
    risk_level          TEXT CHECK (risk_level IN ('critical','high','medium','low',NULL)),

    evidence_present    TEXT[],
    evidence_required   TEXT[],

    remediation_status  TEXT NOT NULL DEFAULT 'open'
        CHECK (remediation_status IN ('open','in_progress','closed','accepted_risk')),
    owner               UUID REFERENCES users(id),
    target_date         DATE,

    source              TEXT NOT NULL DEFAULT 'Not assessed'
        CHECK (source IN ('chat','questionnaire','document','assessor',
                          'self_reported','Not assessed')),
    chat_session_id     TEXT,
    assessed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, standard_id, control_ref)
);

CREATE INDEX IF NOT EXISTS idx_posture_tenant      ON posture_controls (tenant_id);
CREATE INDEX IF NOT EXISTS idx_posture_finding     ON posture_controls (tenant_id, finding);
CREATE INDEX IF NOT EXISTS idx_posture_remediation ON posture_controls (tenant_id, remediation_status)
    WHERE remediation_status != 'closed';

-- Append-only audit trail — NEVER UPDATE OR DELETE
-- Partitioned by year for retention management
-- expires_at stored as regular column (not generated — immutability constraint)
CREATE TABLE IF NOT EXISTS posture_history (
    id              UUID    NOT NULL DEFAULT gen_random_uuid(),
    control_id      UUID    NOT NULL REFERENCES posture_controls(id),
    tenant_id       UUID    NOT NULL,
    finding         TEXT    NOT NULL,
    confidence      TEXT    NOT NULL,
    gap_description TEXT,
    action_required TEXT,
    source          TEXT    NOT NULL,
    chat_session_id TEXT,
    established_via TEXT,
    changed_by      UUID    REFERENCES users(id),
    changed_by_role TEXT,
    confirmed_by    UUID    REFERENCES users(id),
    confirmed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,           -- set at insert: created_at + 3 years
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS posture_history_2025
    PARTITION OF posture_history
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE IF NOT EXISTS posture_history_2026
    PARTITION OF posture_history
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE IF NOT EXISTS posture_history_2027
    PARTITION OF posture_history
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
CREATE TABLE IF NOT EXISTS posture_history_2028
    PARTITION OF posture_history
    FOR VALUES FROM ('2028-01-01') TO ('2029-01-01');

CREATE INDEX IF NOT EXISTS idx_history_control
    ON posture_history (control_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_tenant
    ON posture_history (tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_expiry
    ON posture_history (expires_at);

CREATE TABLE IF NOT EXISTS posture_pending (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    control_id          UUID NOT NULL REFERENCES posture_controls(id),
    proposed_finding    TEXT NOT NULL,
    proposed_gap        TEXT,
    proposed_action     TEXT,
    proposed_confidence TEXT NOT NULL DEFAULT 'medium',
    extraction_source   TEXT,
    extraction_rationale TEXT,
    status              TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','confirmed','rejected','modified')),
    client_note         TEXT,
    resolved_by         UUID REFERENCES users(id),
    resolved_at         TIMESTAMPTZ,
    chat_session_id     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pending_tenant  ON posture_pending (tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_pending_control ON posture_pending (control_id, status);


-- =============================================================================
-- DOCUMENT DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS client_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id),
    filename            TEXT NOT NULL,
    storage_path        TEXT NOT NULL,
    file_size_bytes     INT,
    mime_type           TEXT,
    checksum_sha256     TEXT,
    document_type       TEXT,
    document_title      TEXT,
    version             TEXT,
    full_text           TEXT,           -- nullable: NULL when text is in S3
    page_count          INT,
    approved_by         TEXT,
    approval_date       DATE,
    review_date         DATE,
    document_owner      TEXT,
    topics_detected     TEXT[],
    standards_cited     TEXT[],
    control_refs        TEXT[],
    superseded_by       UUID REFERENCES client_documents(id),
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    uploaded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by         UUID REFERENCES users(id),
    chat_session_id     TEXT,
    expires_at          TIMESTAMPTZ,    -- set at insert per retention_policies
    archived_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_docs_tenant   ON client_documents (tenant_id, is_current);
CREATE INDEX IF NOT EXISTS idx_docs_type     ON client_documents (tenant_id, document_type)
    WHERE is_current;
CREATE INDEX IF NOT EXISTS idx_docs_controls ON client_documents USING GIN (control_refs)
    WHERE is_current;

CREATE TABLE IF NOT EXISTS document_sections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES client_documents(id),
    tenant_id       UUID NOT NULL,
    section_number  TEXT,
    title           TEXT,
    text            TEXT NOT NULL,
    page_start      INT,
    page_end        INT,
    char_offset     INT
);

CREATE INDEX IF NOT EXISTS idx_sections_doc ON document_sections (document_id);

CREATE TABLE IF NOT EXISTS document_findings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL,
    document_id         UUID NOT NULL REFERENCES client_documents(id),
    control_ref         TEXT NOT NULL,
    standard_id         TEXT NOT NULL,
    checklist_item_id   TEXT,
    status              TEXT NOT NULL
        CHECK (status IN ('present','missing','partial')),
    confidence          TEXT NOT NULL DEFAULT 'medium'
        CHECK (confidence IN ('high','medium','low')),
    excerpt             TEXT,
    section_number      TEXT,
    page_number         INT,
    requirement_text    TEXT,
    gdpr_required       BOOLEAN DEFAULT FALSE,
    extracted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_by        UUID REFERENCES users(id),
    confirmed_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ    -- set at insert: extracted_at + 3 years
);

CREATE INDEX IF NOT EXISTS idx_findings_tenant_control
    ON document_findings (tenant_id, control_ref, status);
CREATE INDEX IF NOT EXISTS idx_findings_document
    ON document_findings (document_id);
CREATE INDEX IF NOT EXISTS idx_findings_pending
    ON document_findings (tenant_id)
    WHERE confirmed_at IS NULL;


-- =============================================================================
-- INCIDENT DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS incidents (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenants(id),
    incident_type           TEXT NOT NULL,
    title                   TEXT,
    description             TEXT,
    status                  TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open','in_progress','closed','withdrawn')),
    severity                TEXT NOT NULL DEFAULT 'medium'
        CHECK (severity IN ('critical','high','medium','low')),
    occurred_at             TIMESTAMPTZ,
    reported_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deadline_at             TIMESTAMPTZ,
    notified_at             TIMESTAMPTZ,
    closed_at               TIMESTAMPTZ,
    affected_count_approx   INT,
    affected_categories     TEXT[],
    affected_countries      TEXT[],
    neo4j_node_id           TEXT,
    neo4j_synced            BOOLEAN NOT NULL DEFAULT FALSE,
    created_by              UUID REFERENCES users(id),
    chat_session_id         TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at              TIMESTAMPTZ  -- set at insert: reported_at + 5 years
);

CREATE INDEX IF NOT EXISTS idx_incidents_tenant
    ON incidents (tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_incidents_type
    ON incidents (tenant_id, incident_type, status);
CREATE INDEX IF NOT EXISTS idx_incidents_deadline
    ON incidents (tenant_id, deadline_at)
    WHERE status IN ('open','in_progress');
CREATE INDEX IF NOT EXISTS idx_incidents_expiry
    ON incidents (expires_at);

CREATE TABLE IF NOT EXISTS incident_timeline (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id   UUID NOT NULL,
    event_type  TEXT NOT NULL,
    from_status TEXT,
    to_status   TEXT,
    note        TEXT,
    actioned_by UUID REFERENCES users(id),
    actioned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ  -- set at insert: actioned_at + 5 years
);

CREATE INDEX IF NOT EXISTS idx_timeline_incident
    ON incident_timeline (incident_id, actioned_at DESC);

CREATE TABLE IF NOT EXISTS incident_documents (
    incident_id   UUID NOT NULL REFERENCES incidents(id),
    document_id   UUID NOT NULL REFERENCES client_documents(id),
    tenant_id     UUID NOT NULL REFERENCES tenants(id),
    document_role TEXT NOT NULL
        CHECK (document_role IN
            ('notification','evidence','response','correspondence','dpa')),
    linked_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    linked_by     UUID REFERENCES users(id),
    PRIMARY KEY (incident_id, document_id)
);

CREATE TABLE IF NOT EXISTS incident_obligations (
    incident_id UUID NOT NULL REFERENCES incidents(id),
    tenant_id   UUID NOT NULL REFERENCES tenants(id),
    control_ref TEXT NOT NULL,
    standard_id TEXT NOT NULL,
    deadline    TEXT,
    deadline_at TIMESTAMPTZ,
    rationale   TEXT,
    is_met      BOOLEAN DEFAULT FALSE,
    met_at      TIMESTAMPTZ,
    PRIMARY KEY (incident_id, control_ref, standard_id)
);

CREATE INDEX IF NOT EXISTS idx_incident_obligations_tenant
    ON incident_obligations (tenant_id);


-- =============================================================================
-- REMEDIATION DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS remediation_plans (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID NOT NULL REFERENCES tenants(id),
    control_id   UUID NOT NULL REFERENCES posture_controls(id),
    title        TEXT NOT NULL,
    description  TEXT,
    status       TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','active','completed','cancelled')),
    owner        UUID REFERENCES users(id),
    target_date  DATE,
    created_by   UUID REFERENCES users(id),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_remediation_tenant
    ON remediation_plans (tenant_id, status);

CREATE TABLE IF NOT EXISTS remediation_tasks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id      UUID NOT NULL REFERENCES remediation_plans(id),
    tenant_id    UUID NOT NULL,
    title        TEXT NOT NULL,
    description  TEXT,
    status       TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open','in_progress','done','skipped')),
    owner        UUID REFERENCES users(id),
    due_date     DATE,
    completed_at TIMESTAMPTZ,
    effort_hours NUMERIC(5,1)
);

CREATE TABLE IF NOT EXISTS remediation_evidence (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      UUID NOT NULL REFERENCES remediation_tasks(id),
    tenant_id    UUID NOT NULL REFERENCES tenants(id),
    document_id  UUID REFERENCES client_documents(id),
    note         TEXT,
    submitted_by UUID REFERENCES users(id),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================================
-- NOTIFICATIONS DOMAIN
-- =============================================================================

CREATE TABLE IF NOT EXISTS notifications (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID NOT NULL REFERENCES tenants(id),
    user_id      UUID REFERENCES users(id),
    target_role  TEXT REFERENCES roles(name),
    type         TEXT NOT NULL,
    severity     TEXT NOT NULL DEFAULT 'info'
        CHECK (severity IN ('info','warning','urgent','critical')),
    title        TEXT NOT NULL,
    body         TEXT NOT NULL,
    action_url   TEXT,
    source_table TEXT,
    source_id    UUID,
    delivered_at TIMESTAMPTZ,
    read_at      TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_notifications_user
    ON notifications (user_id)   WHERE read_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_tenant
    ON notifications (tenant_id, type) WHERE dismissed_at IS NULL;


-- =============================================================================
-- RETENTION POLICIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS retention_policies (
    table_name       TEXT PRIMARY KEY,
    retention_years  INT  NOT NULL,
    warn_days_before INT  NOT NULL DEFAULT 90,
    action           TEXT NOT NULL DEFAULT 'archive'
        CHECK (action IN ('archive','delete')),
    last_run_at      TIMESTAMPTZ,
    last_run_count   INT,
    notes            TEXT
);

INSERT INTO retention_policies
    (table_name, retention_years, warn_days_before, action, notes)
VALUES
('posture_history',    3, 90,  'archive', 'ISO 27001 evidence — 3 year minimum'),
('document_findings',  3, 90,  'archive', 'ISO 27001 evidence'),
('client_documents',   3, 90,  'archive', 'Policy versions — archive superseded'),
('incidents',          5, 180, 'archive', 'GDPR breach records — 5 year minimum'),
('incident_timeline',  5, 180, 'archive', 'GDPR breach records'),
('notifications',      1, 30,  'delete',  'Operational — purge after 1 year'),
('audit_log',          7, 180, 'archive', 'General audit log — 7 years')
ON CONFLICT (table_name) DO NOTHING;


-- =============================================================================
-- AUDIT LOG
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID        NOT NULL DEFAULT gen_random_uuid(),
    tenant_id       UUID,
    user_id         UUID,
    user_role       TEXT,
    action          TEXT        NOT NULL,
    table_name      TEXT        NOT NULL,
    record_id       UUID        NOT NULL,
    old_values      JSONB,
    new_values      JSONB,
    changed_fields  TEXT[],
    ip_address      INET,
    user_agent      TEXT,
    chat_session_id TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS audit_log_2025
    PARTITION OF audit_log FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE IF NOT EXISTS audit_log_2026
    PARTITION OF audit_log FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE IF NOT EXISTS audit_log_2027
    PARTITION OF audit_log FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
CREATE TABLE IF NOT EXISTS audit_log_2028
    PARTITION OF audit_log FOR VALUES FROM ('2028-01-01') TO ('2029-01-01');

CREATE INDEX IF NOT EXISTS idx_audit_tenant
    ON audit_log (tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_record
    ON audit_log (table_name, record_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user
    ON audit_log (user_id, created_at DESC);


-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

DO $$ DECLARE t TEXT;
BEGIN
    -- Note: posture_history and audit_log are partitioned tables.
    -- RLS on the parent table propagates to all partitions automatically.
    FOR t IN SELECT unnest(ARRAY[
        'users','user_roles','applicable_standards','client_facts',
        'posture_controls','posture_pending',
        'client_documents','document_sections','document_findings',
        'incidents','incident_timeline','incident_documents','incident_obligations',
        'remediation_plans','remediation_tasks','remediation_evidence',
        'notifications'
    ]) LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        BEGIN
            EXECUTE format(
                'CREATE POLICY tenant_isolation ON %I
                 USING (tenant_id = current_setting(''app.tenant_id'', TRUE)::uuid)',
                t
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END;
    END LOOP;
END $$;

-- Partitioned tables — enable RLS on parent only
ALTER TABLE posture_history ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    CREATE POLICY tenant_isolation ON posture_history
        USING (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    CREATE POLICY tenant_isolation ON audit_log
        USING (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    CREATE POLICY tenant_self ON tenants
        USING (id = current_setting('app.tenant_id', TRUE)::uuid);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE retention_policies ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    CREATE POLICY retention_read ON retention_policies FOR SELECT USING (TRUE);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    CREATE POLICY roles_read ON roles FOR SELECT USING (TRUE);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- =============================================================================
-- VIEWS
-- =============================================================================

CREATE OR REPLACE VIEW v_posture_summary AS
SELECT
    tenant_id,
    COUNT(*)                                         AS total_controls,
    COUNT(*) FILTER (WHERE finding = 'NC')           AS nc_count,
    COUNT(*) FILTER (WHERE finding = 'OFI')          AS ofi_count,
    COUNT(*) FILTER (WHERE finding = 'Comply')       AS comply_count,
    COUNT(*) FILTER (WHERE finding = 'Not assessed') AS unassessed_count,
    COUNT(*) FILTER (WHERE finding = 'N/A')          AS na_count,
    ROUND(
        COUNT(*) FILTER (WHERE finding = 'Comply')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE finding != 'Not assessed'), 0) * 100,
    1) AS comply_percentage,
    MAX(last_updated) AS last_updated
FROM posture_controls
GROUP BY tenant_id;

CREATE OR REPLACE VIEW v_incidents_open AS
SELECT
    i.*,
    CASE
        WHEN i.deadline_at IS NULL                        THEN NULL
        ELSE EXTRACT(EPOCH FROM (i.deadline_at - NOW()))/3600
    END AS hours_remaining,
    CASE
        WHEN i.deadline_at IS NULL                        THEN 'no_deadline'
        WHEN i.deadline_at < NOW()                        THEN 'overdue'
        WHEN i.deadline_at < NOW() + INTERVAL '12 hours' THEN 'critical'
        WHEN i.deadline_at < NOW() + INTERVAL '48 hours' THEN 'urgent'
        WHEN i.deadline_at < NOW() + INTERVAL '7 days'   THEN 'soon'
        ELSE 'on_track'
    END AS urgency
FROM incidents i
WHERE i.status IN ('open','in_progress');

CREATE OR REPLACE VIEW v_audit_evidence AS
SELECT
    pc.tenant_id,
    pc.standard_id,
    pc.control_ref,
    pc.node_id,
    pc.finding,
    pc.confidence,
    pc.gap_description,
    pc.action_required,
    pc.evidence_present,
    pc.remediation_status,
    pc.target_date,
    pc.source,
    pc.assessed_at,
    cd.filename,
    cd.version             AS document_version,
    cd.approved_by,
    cd.approval_date,
    df.status              AS evidence_status,
    df.excerpt             AS evidence_excerpt,
    df.section_number,
    df.page_number,
    df.requirement_text,
    df.gdpr_required,
    df.confirmed_by        AS evidence_confirmed_by,
    df.confirmed_at        AS evidence_confirmed_at
FROM posture_controls pc
LEFT JOIN document_findings df
    ON  df.tenant_id   = pc.tenant_id
    AND df.control_ref = pc.control_ref
    AND df.status      = 'present'
    AND df.confirmed_at IS NOT NULL
LEFT JOIN client_documents cd
    ON  cd.id          = df.document_id
    AND cd.is_current  = TRUE;

CREATE OR REPLACE VIEW v_retention_warnings AS
SELECT
    'posture_history' AS source_table,
    tenant_id::TEXT,
    id::TEXT          AS record_id,
    created_at        AS record_date,
    expires_at,
    EXTRACT(DAY FROM expires_at - NOW())::INT AS days_remaining
FROM posture_history
WHERE expires_at BETWEEN NOW() AND NOW() + INTERVAL '90 days'
UNION ALL
SELECT
    'incidents',
    tenant_id::TEXT,
    id::TEXT,
    reported_at,
    expires_at,
    EXTRACT(DAY FROM expires_at - NOW())::INT
FROM incidents
WHERE expires_at IS NOT NULL
  AND expires_at BETWEEN NOW() AND NOW() + INTERVAL '180 days'
ORDER BY days_remaining;

