-- schema_v73_ship3g_cite_verification_overdue.sql
--
-- Ship 3'.g (2026-07-17) — cite-mode verification overdue sweep.
--
-- Adds one notification kind + one sweep work_type + one RLS grant:
--
--   Notification kind: `cite_verification_overdue`
--     Fires when an active `external_evidence_source.next_review_due`
--     has passed without a fresh `external_evidence_verification_log`
--     entry bumping `last_verified_at` + `next_review_due` forward.
--     Auditor-critical: cited evidence without recent verification is
--     worse than stale stored evidence (no artefact in-product at all).
--
--   Sweep work_type: `cite_verification_overdue`
--     Registered in `rag/scheduler/tick.py::sweep_cite_verification_overdue`.
--     Fires on the 30-min systemd timer alongside freshness_expiry
--     + overdue_followups (Ships 3'.b + 3'.f).
--
--   RLS: `app_external_evidence_source_all` permissive policy for
--     arioncomply_app on external_evidence_source — same pattern as
--     schema_v70 (tenant_notification) + v72 (cascade tables). Sweep
--     needs cross-tenant read to iterate overdue rows.

BEGIN;

-- 1. Extend tenant_notification.kind CHECK
ALTER TABLE tenant_notification
    DROP CONSTRAINT IF EXISTS tenant_notification_kind_check;

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
        'cite_verification_overdue'
    ]));

COMMENT ON COLUMN tenant_notification.kind IS
'Notification category. Kind added in Ship 3''.g (2026-07-17): cite_verification_overdue (an active external_evidence_source has passed its next_review_due without a fresh verification log entry — sweep-driven by rag/scheduler/tick.py::sweep_cite_verification_overdue).';

-- 2. Extend sweep_log.work_type CHECK
ALTER TABLE sweep_log
    DROP CONSTRAINT IF EXISTS sweep_log_work_type_check;

ALTER TABLE sweep_log
    ADD CONSTRAINT sweep_log_work_type_check
    CHECK (work_type = ANY (ARRAY[
        'fact_recompute',
        'overdue_followups',
        'freshness_expiry',
        'notification_delivery',
        'engine_kick',
        'cite_verification_overdue',
        'other'
    ]));

-- 3. Permissive RLS for arioncomply_app cross-tenant read on cite sources
DROP POLICY IF EXISTS app_external_evidence_source_all ON external_evidence_source;
CREATE POLICY app_external_evidence_source_all ON external_evidence_source
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

COMMIT;
