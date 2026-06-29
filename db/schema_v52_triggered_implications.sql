-- schema_v52_triggered_implications.sql — S3 cascade-engine output
--
-- Implements the implications-tracking layer per
-- [Relationship model design §6](docs/relationship_model_design_2026_06_29.md)
-- and the meditation patterns P1 (event emits event) + P9 (cascade
-- depth budget) + P10 (implication grouping for the human surface).
--
-- When a tenant submits a verification with structured_events, the
-- cascade engine walks Neo4j:
--   Event -[:TRIGGERS_OBLIGATION]-> RequirementNode  (direct, 1-hop)
--   Event -[:EMITS_EVENT]->         Event             (recurse, cap=4)
-- and inserts one row per (downstream event, target obligation) pair.
--
-- Each implication carries a due_date computed from the
-- TRIGGERS_OBLIGATION edge's `deadline` property (parsed) +
-- the verification's verified_at as the start of the clock.
--
-- Lifecycle: pending -> satisfied | dismissed
-- Overdue is computed at READ time (now() > due_date AND status='pending').
--
-- All RLS-scoped to tenant_id.

BEGIN;

CREATE TABLE IF NOT EXISTS triggered_implication (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID         NOT NULL,

    -- ── Source: the verification that fired this implication ──
    source_verification_id UUID         NOT NULL
        REFERENCES external_evidence_verification_log(id) ON DELETE CASCADE,
    source_event_type      TEXT         NOT NULL,
    -- e.g. 'personnel_added' — the cascade started here. May be a
    -- top-level emission (direct from structured_events) or an
    -- intermediate emission (via Event-EMITS_EVENT->Event).

    cascade_path           JSONB        NOT NULL DEFAULT '[]'::jsonb,
    -- Array of event_types in emission order, e.g.
    --   ["asset_lost_stolen", "information_security_incident", "personal_data_breach"]
    -- Length 1 for direct emissions. Length<=4 per P9.

    cascade_depth          INTEGER      NOT NULL DEFAULT 0,
    -- 0 = direct from structured_events; 1+ = via EMITS_EVENT hops.

    -- ── Target: the obligation that must be acted on ──
    target_control_ref     TEXT         NOT NULL,
    -- e.g. 'A.6.3' or 'Art.32' — parsed from RequirementNode.id
    target_standard_id     TEXT         NOT NULL,
    -- e.g. 'ISO27001:2022' or 'GDPR:2016/679'
    target_requirement_id  TEXT         NOT NULL,
    -- The full RequirementNode.id, e.g. 'ISO27001:2022:A.6.3'

    -- ── Lifecycle ──
    expected_action        TEXT         NOT NULL DEFAULT 'evidence_required',
    -- Sketch for v1: 'evidence_required' / 'review_required' /
    -- 'attestation_required'. v1 always defaults to evidence_required.

    fired_at               TIMESTAMPTZ  NOT NULL DEFAULT now(),
    -- When the cascade engine wrote this row. May lag verified_at if
    -- engine is async (v1: synchronous, fired_at ≈ verified_at).

    due_date               TIMESTAMPTZ,
    -- Computed from the TRIGGERS_OBLIGATION edge's deadline property
    -- + the source verification's verified_at. NULL when deadline is
    -- absent (e.g. "no headline deadline" obligations).

    status                 TEXT         NOT NULL DEFAULT 'pending',
    -- pending | satisfied | dismissed
    -- 'overdue' is NOT stored — it's derived at read time.

    -- ── Resolution payload ──
    resolved_at            TIMESTAMPTZ,
    resolved_by            UUID,
    resolved_evidence_kind TEXT,
    -- 'finding' | 'cite' | 'dismissal' | NULL
    resolved_evidence_id   UUID,
    dismissed_reason       TEXT,
    -- REQUIRED when status='dismissed' (CHECK enforced below). The
    -- auditor wants to know WHY a tenant ignored an implication.

    -- ── Optional metadata ──
    rationale              TEXT,
    -- Copy of the TRIGGERS_OBLIGATION edge's rationale snapshot at
    -- fire time (so the row is auditor-readable even if the edge is
    -- later re-curated).
    deadline_string        TEXT,
    -- The raw deadline string from the trigger edge (e.g. "72h",
    -- "30 days") preserved alongside the computed due_date for
    -- traceability.

    -- ── Constraints ──
    CONSTRAINT triggered_implication_status_chk
        CHECK (status IN ('pending', 'satisfied', 'dismissed')),
    CONSTRAINT triggered_implication_resolution_consistent CHECK (
        (status = 'pending'   AND resolved_at IS NULL AND dismissed_reason IS NULL)
        OR
        (status = 'satisfied' AND resolved_at IS NOT NULL)
        OR
        (status = 'dismissed' AND resolved_at IS NOT NULL
                              AND dismissed_reason IS NOT NULL
                              AND length(trim(dismissed_reason)) > 0)
    ),
    CONSTRAINT triggered_implication_depth_chk
        CHECK (cascade_depth >= 0 AND cascade_depth <= 4),
    CONSTRAINT triggered_implication_expected_action_chk
        CHECK (expected_action IN ('evidence_required',
                                   'review_required',
                                   'attestation_required'))
);

-- ── Indexes ──
CREATE INDEX IF NOT EXISTS idx_triggered_implication_tenant_status_due
    ON triggered_implication(tenant_id, status, due_date NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_triggered_implication_source
    ON triggered_implication(source_verification_id);

CREATE INDEX IF NOT EXISTS idx_triggered_implication_target
    ON triggered_implication(tenant_id, target_requirement_id);

-- Partial index for the most-common read path: pending implications
-- past or near their due date.
CREATE INDEX IF NOT EXISTS idx_triggered_implication_pending_due
    ON triggered_implication(tenant_id, due_date)
    WHERE status = 'pending' AND due_date IS NOT NULL;

-- ── RLS ──
ALTER TABLE triggered_implication ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON triggered_implication;
CREATE POLICY tenant_isolation ON triggered_implication
    USING (tenant_id::text = current_setting('app.tenant_id', TRUE));

GRANT SELECT, INSERT, UPDATE ON triggered_implication TO arioncomply_app;
-- No DELETE grant: implications are append-only at the lifecycle
-- level. Closure happens through UPDATE setting status + resolved_at.
-- Hard deletes only via DB admin (audit-integrity).

COMMENT ON TABLE triggered_implication IS
    'Per-tenant cascade-engine output. One row per (downstream event, target obligation) pair fired by a verification.';

COMMENT ON COLUMN triggered_implication.cascade_path IS
    'Ordered list of event_types in the emission chain. Length 1 = direct from structured_events. Up to 4 per the depth cap (P9 from cascade meditation).';

COMMENT ON COLUMN triggered_implication.due_date IS
    'verified_at + parsed(deadline). NULL when the trigger edge has no headline deadline. The reader treats now() > due_date AND status=pending as overdue.';

COMMENT ON COLUMN triggered_implication.dismissed_reason IS
    'Required when status=dismissed (CHECK enforced). Auditor-grade explanation of why this implication was deemed inapplicable / already-addressed / superseded.';

COMMIT;
