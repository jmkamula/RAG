-- schema_v74_ship3i_producer_kinds.sql
--
-- Ship 3'.i (2026-07-17) — final two notification producer kinds.
--
-- Adds:
--   posture_flip_to_comply — live posture transitioned INTO Comply
--                            from a non-Comply state. Mirror of
--                            Ship 3'.c's nc_surfaced; fires from
--                            rag/intake/posture_writer.py::_log_status_change.
--                            Positive-news notification (severity 'low').
--   api_key_expiring       — an API key is approaching its expires_at
--                            date. Sweep-driven; buckets at 30d, 7d,
--                            and 1d; dedup by bucket so tenant gets
--                            three escalating heads-up rather than a
--                            daily nag.
--
-- Also registers the new `api_key_expiring` sweep work_type.

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
        'cite_verification_overdue',
        'posture_flip_to_comply',
        'api_key_expiring'
    ]));

COMMENT ON COLUMN tenant_notification.kind IS
'Notification category. Kinds added in Ship 3''.i (2026-07-17): posture_flip_to_comply (mirror of nc_surfaced — fires when live finding transitions into Comply from non-Comply); api_key_expiring (sweep-driven — buckets at 30d/7d/1d before api_keys.expires_at).';

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
        'api_key_expiring',
        'other'
    ]));

-- 3. api_keys already has expires_at (nullable) + app_all_api_keys
--    permissive policy for arioncomply_app. No schema change needed
--    for the sweep to read across tenants.

COMMIT;
