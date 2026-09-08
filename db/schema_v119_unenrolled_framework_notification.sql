-- schema_v119_unenrolled_framework_notification.sql
--
-- Ship 129'.d (2026-09-08) — one new notification kind + one new
-- sweep work_type. Closes the "how does a tenant learn they should
-- enrol GDPR when they process EU data" loop.
--
-- Rule of thumb established in Ship 129':
--   Discovery persists universally (framework-agnostic).
--   Evidence surfaces strictly by tenant_standards enrolment.
--   Nudges are driven by jurisdiction facts (client_facts), NOT by
--   discovery counts. Counts enrich the notification body but never
--   drive the trigger.
--
-- See rag/notifications/enrolment_nudge.py.

BEGIN;

-- ── Extend the notification kind allowlist ──────────────────────────
ALTER TABLE tenant_notification
    DROP CONSTRAINT tenant_notification_kind_check;

ALTER TABLE tenant_notification
    ADD CONSTRAINT tenant_notification_kind_check
    CHECK (kind = ANY (ARRAY[
        'implication_overdue',
        'followup_overdue',
        'threshold_crossed',
        'cascade_blocked',
        'auto_resolved',
        'freshness_expiry',
        'nc_surfaced',
        'upload_processed',
        'stage2_proposal_ready',
        'upload_failed',
        'cite_verification_overdue',
        'posture_flip_to_comply',
        'api_key_expiring',
        'risk_added',
        'risk_treatment_overdue',
        'residual_above_threshold',
        'risk_review_due',
        -- Ship 129'.d addition
        'unenrolled_framework_applicable'
    ]));

-- ── Extend the sweep work_type allowlist ────────────────────────────
ALTER TABLE sweep_log
    DROP CONSTRAINT sweep_log_work_type_check;

ALTER TABLE sweep_log
    ADD CONSTRAINT sweep_log_work_type_check
    CHECK (work_type = ANY (ARRAY[
        'fact_recompute',
        'overdue_followups',
        'freshness_expiry',
        'notification_delivery',
        'engine_kick',
        'cite_verification_overdue',
        'api_key_expiring',
        'notification_retention',
        'risk_register_notify',
        -- Pre-existing values in _WORK_TYPES but missing from earlier
        -- CHECK constraints — captured here so the constraint matches
        -- the sweep_log data on the dev VM.
        'posture_refresh',
        'cite_attestation_retention',
        -- Ship 129'.d addition
        'enrolment_nudge',
        'other'
    ]));

COMMIT;

-- Verification:
--   \d tenant_notification
--     → tenant_notification_kind_check now shows 18 allowed values.
--   \d sweep_log
--     → sweep_log_work_type_check now shows 11 allowed values.
