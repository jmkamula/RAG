-- =============================================================================
-- schema_v25_hitl_confirmation_guard.sql
--
-- Extends fn_posture_confirmation_guard to permit the two HITL transitions
-- introduced by v24:
--
--   any state → 'document_confirmed'   (Stage-1 batch approval)
--   any state → 'engine_confirmed'     (Stage-2 engine-verdict approval)
--
-- v24 added these states to the confirmation_status CHECK constraint, but the
-- trigger function from db/schema_v7_phase2b.sql still raised on any
-- transition outside the v7 vocabulary (draft↔confirmed, *→overridden). That
-- blocked stage1_review_chat.approve_findings_for_control and
-- stage2_approval_chat.approve_engine_proposal from persisting their writes.
--
-- Idempotent: CREATE OR REPLACE FUNCTION rebinds the existing trigger.
-- =============================================================================

-- ----------------------------------------------------------------------------
-- 1) Per-tenant chat-surface user. confirmation_log.performed_by is NOT NULL
--    and the Stage-1/Stage-2 chat surfaces don't yet carry a session-bound
--    user id — until that wiring lands, all batch approvals are credited to
--    the per-tenant chat-user placeholder. Email pattern stays globally
--    unique because tenant_id is interpolated; format remains RFC-5321-valid
--    (dashes only, no extra '@'). The trigger falls back to this user when
--    neither NEW.confirmed_by nor app.user_id is set.
-- ----------------------------------------------------------------------------

INSERT INTO users (id, tenant_id, email, full_name, retention_class)
SELECT gen_random_uuid(),
       t.id,
       'chat-user-' || t.id::text || '@arioncomply.internal',
       'ArionComply Chat Surface',
       'operational'
  FROM tenants t
 WHERE NOT EXISTS (
     SELECT 1 FROM users u
      WHERE u.tenant_id = t.id
        AND u.email = 'chat-user-' || t.id::text || '@arioncomply.internal'
 );

-- ----------------------------------------------------------------------------
-- 2) confirmation_log.action CHECK must accept the two new actions written by
--    the extended trigger. The v7 vocabulary is preserved.
--    posture_controls.source CHECK must accept 'engine' so the Stage-2
--    chat surface can mark engine-approved rows as engine-sourced
--    (per [[hitl-two-stage-approval-design]] — engine verdicts overwrite
--    finding only after explicit approval).
-- ----------------------------------------------------------------------------

ALTER TABLE confirmation_log
    DROP CONSTRAINT IF EXISTS confirmation_log_action_check;
ALTER TABLE confirmation_log
    ADD CONSTRAINT confirmation_log_action_check
    CHECK (action IN (
        'confirmed',
        'reverted_to_draft',
        'overridden',
        'bulk_confirmed',
        'document_confirmed',
        'engine_confirmed'
    ));

ALTER TABLE posture_controls
    DROP CONSTRAINT IF EXISTS posture_controls_source_check;
ALTER TABLE posture_controls
    ADD CONSTRAINT posture_controls_source_check
    CHECK (source IN (
        'chat', 'questionnaire', 'document', 'assessor',
        'self_reported', 'workbook', 'Not assessed',
        'engine'
    ));

-- ----------------------------------------------------------------------------
-- 3) Trigger function: add transitions for the two HITL gates.
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_posture_confirmation_guard()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id   UUID;
    v_action    TEXT;
BEGIN
    v_user_id := NULLIF(current_setting('app.user_id', TRUE), '')::UUID;

    IF OLD.confirmation_status = NEW.confirmation_status THEN
        RETURN NEW;
    END IF;

    -- draft → confirmed: requires a confirmed_by user (v7 contract preserved).
    IF OLD.confirmation_status = 'draft'
       AND NEW.confirmation_status = 'confirmed' THEN
        IF NEW.confirmed_by IS NULL AND v_user_id IS NULL THEN
            RAISE EXCEPTION
                'Cannot confirm posture control % without a confirmed_by user',
                NEW.id
            USING ERRCODE = '23514';
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'confirmed';

    -- confirmed → draft: allowed when new evidence invalidates a confirmation.
    ELSIF OLD.confirmation_status = 'confirmed'
          AND NEW.confirmation_status = 'draft' THEN
        NEW.confirmed_by := NULL;
        NEW.confirmed_at := NULL;
        v_action := 'reverted_to_draft';

    -- any → overridden: human override path (v7 contract preserved).
    ELSIF NEW.confirmation_status = 'overridden' THEN
        IF NEW.system_finding IS NULL THEN
            NEW.system_finding     := OLD.finding;
            NEW.system_gap         := OLD.gap_description;
            NEW.system_proposed_at := OLD.updated_at;
        END IF;
        NEW.confirmed_by := COALESCE(NEW.confirmed_by, v_user_id);
        NEW.confirmed_at := NOW();
        v_action := 'overridden';

    -- HITL Stage-1: any → document_confirmed
    -- Performer resolution: explicit NEW.confirmed_by → app.user_id setting →
    -- per-tenant chat-user fallback (seeded above). The fallback keeps
    -- confirmation_log.performed_by NOT NULL satisfied until session-bound
    -- user ids land.
    ELSIF NEW.confirmation_status = 'document_confirmed' THEN
        NEW.confirmed_by := COALESCE(
            NEW.confirmed_by,
            v_user_id,
            (SELECT id FROM users
              WHERE tenant_id = NEW.tenant_id
                AND email = 'chat-user-' || NEW.tenant_id::text
                            || '@arioncomply.internal'
              LIMIT 1)
        );
        NEW.confirmed_at := NOW();
        v_action := 'document_confirmed';

    -- HITL Stage-2: any → engine_confirmed
    -- Same performer fallback as Stage-1. The Stage-2 chat surface also
    -- writes engine_approved_by / engine_approved_at separately on the
    -- posture_controls row; the confirmation_log entry captures the same
    -- performer for cross-table joins.
    ELSIF NEW.confirmation_status = 'engine_confirmed' THEN
        NEW.confirmed_by := COALESCE(
            NEW.confirmed_by,
            v_user_id,
            (SELECT id FROM users
              WHERE tenant_id = NEW.tenant_id
                AND email = 'chat-user-' || NEW.tenant_id::text
                            || '@arioncomply.internal'
              LIMIT 1)
        );
        NEW.confirmed_at := NOW();
        v_action := 'engine_confirmed';

    ELSE
        RAISE EXCEPTION
            'Invalid confirmation state transition: % → % for control %',
            OLD.confirmation_status, NEW.confirmation_status, NEW.control_ref
        USING ERRCODE = '23514';
    END IF;

    INSERT INTO confirmation_log (
        tenant_id, posture_control_id, control_ref, standard_id,
        action, previous_status, new_status,
        previous_finding, new_finding,
        performed_by, source
    ) VALUES (
        NEW.tenant_id, NEW.id, NEW.control_ref, NEW.standard_id,
        v_action, OLD.confirmation_status, NEW.confirmation_status,
        OLD.finding, NEW.finding,
        COALESCE(NEW.confirmed_by, v_user_id),
        NEW.source
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
