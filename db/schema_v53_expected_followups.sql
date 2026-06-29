-- schema_v53_expected_followups.sql — S3b followup enforcement
--
-- Implements meditation pattern P2 (missing-event detection): when an
-- Event A has EXPECTS_FOLLOWUP_EVENT edges to Event B, firing A
-- creates an expected_followup_event row tracking the expectation.
-- A periodic sweep flags rows whose window has elapsed without a
-- matching downstream verification.
--
-- Example flow:
--   tenant verifies HR cite with structured_events=[personnel_offboarded × 1]
--   -> A.5.16 / A.5.17 / A.5.18 obligations fire (TRIGGERS_OBLIGATION, S3)
--   -> ALSO: expected_followup_event row INSERTed expecting privilege_revoked
--      within 1 day (from EXPECTS_FOLLOWUP_EVENT edge in Neo4j)
--   tenant later verifies IAM cite with structured_events=[privilege_revoked × 1]
--   -> followup matched, row marked status=satisfied
--   if no matching verification arrives within window:
--   -> sweep marks row status=overdue, fires implication on the SLA-met MUST

BEGIN;

CREATE TABLE IF NOT EXISTS expected_followup_event (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    -- ── Source: which verification created this expectation ──
    source_verification_id UUID         NOT NULL
        REFERENCES external_evidence_verification_log(id) ON DELETE CASCADE,
    source_event_type      TEXT         NOT NULL,
    -- e.g. 'personnel_offboarded'

    -- ── Expected followup ──
    expected_event_type    TEXT         NOT NULL,
    -- e.g. 'privilege_revoked' — must match Event.event_type in Neo4j
    window_days            INTEGER      NOT NULL,
    -- e.g. 1 for offboarding SLA; from EXPECTS_FOLLOWUP_EVENT edge prop

    -- ── Lifecycle ──
    fired_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),
    expires_at             TIMESTAMPTZ  NOT NULL,
    -- fired_at + window_days days. Sweep compares against now().

    status                 TEXT         NOT NULL DEFAULT 'pending',
    -- pending | satisfied | overdue
    -- 'overdue' is set by the sweep when expires_at < now() AND no
    -- matching verification arrived. Distinct from triggered_implication's
    -- status because the expectation is about WHETHER a downstream event
    -- arrived, not whether an obligation got evidence.

    resolved_at            TIMESTAMPTZ,
    resolved_verification_id UUID,
    -- The verification whose structured_events satisfied this expectation
    -- (populated when status flips to 'satisfied').
    rationale              TEXT,
    -- Copy of the EXPECTS_FOLLOWUP_EVENT edge's rationale at fire time.

    -- ── Constraints ──
    CONSTRAINT expected_followup_event_status_chk
        CHECK (status IN ('pending', 'satisfied', 'overdue')),
    CONSTRAINT expected_followup_event_window_chk
        CHECK (window_days >= 0 AND window_days <= 3650),
    CONSTRAINT expected_followup_event_resolution_consistent CHECK (
        (status = 'pending' AND resolved_at IS NULL)
        OR
        (status = 'satisfied' AND resolved_at IS NOT NULL
                               AND resolved_verification_id IS NOT NULL)
        OR
        (status = 'overdue' AND resolved_at IS NOT NULL
                             AND resolved_verification_id IS NULL)
    )
);

-- ── Indexes ──
CREATE INDEX IF NOT EXISTS idx_expected_followup_tenant_status_expires
    ON expected_followup_event(tenant_id, status, expires_at);

CREATE INDEX IF NOT EXISTS idx_expected_followup_pending_expired
    ON expected_followup_event(tenant_id, expires_at)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_expected_followup_source
    ON expected_followup_event(source_verification_id);

-- Index used by satisfaction matching: when a new verification arrives
-- with structured_events containing event X, scan for pending rows in
-- this tenant whose expected_event_type = X.
CREATE INDEX IF NOT EXISTS idx_expected_followup_match_target
    ON expected_followup_event(tenant_id, expected_event_type)
    WHERE status = 'pending';

-- ── RLS ──
ALTER TABLE expected_followup_event ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON expected_followup_event;
CREATE POLICY tenant_isolation ON expected_followup_event
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE ON expected_followup_event TO arioncomply_app;

COMMENT ON TABLE expected_followup_event IS
    'Per-tenant tracking of EXPECTS_FOLLOWUP_EVENT chains. Pending row -> awaiting matching downstream verification. Satisfied -> matched. Overdue -> window elapsed without match (sweep-derived).';

COMMIT;
