-- schema_v88_ship14f_risk_register_notifications.sql
--
-- Ship 14'.f (2026-07-22) — 4 new notification kinds for the risk
-- register + 1 new sweep work_type.
--
-- Per Ship 14'.a addendum: risk-register lifecycle events are
-- terminal (they don't propagate to other controls the way
-- incident_declared does), so they surface as PURE notifications,
-- not as cascade implications. No cascade taxonomy edges or Neo4j
-- relationship types are added by this arc.
--
-- Notification kinds:
--   * risk_added              — new row inserted into risks
--   * risk_treatment_overdue  — implementation_date past, status != implemented
--   * residual_above_threshold — residual_risk_level >= 15
--   * risk_review_due         — review_date within 30 days or past
--
-- work_type:
--   * risk_register_notify — sweep that scans the risks table and
--     emits per-tenant notifications for the 3 time-triggered
--     kinds (overdue / above_threshold / review_due). The 4th
--     kind (risk_added) is a write-path producer — fires from
--     the workbook importer / API POST path, not from the sweep.

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
        -- Ship 14'.f additions
        'risk_added',
        'risk_treatment_overdue',
        'residual_above_threshold',
        'risk_review_due'
    ]));

-- ── Sweep-friendly RLS policy on `risks` ──────────────────────────
-- Mirrors `app_posture_all` on posture_controls. The default
-- `tenant_isolation` policy requires `app.tenant_id` to be set on
-- every SELECT; the sweep needs to iterate across all tenants in
-- one query, so it needs a permissive maintenance policy for the
-- `arioncomply_app` role. The `tenant_isolation` policy stays as
-- the default for every OTHER role.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
         WHERE tablename = 'risks' AND policyname = 'app_risk_all'
    ) THEN
        CREATE POLICY app_risk_all ON risks
            TO arioncomply_app
            USING (true) WITH CHECK (true);
    END IF;
END$$;

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
        'risk_register_notify',   -- Ship 14'.f
        'other'
    ]));

COMMIT;

-- Verification:
--   \d tenant_notification
--     → tenant_notification_kind_check now shows 17 allowed values.
--   \d sweep_log
--     → sweep_log_work_type_check now shows 10 allowed values.
