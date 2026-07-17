-- schema_v77_ship3k_retention_work_type.sql
--
-- Ship 3'.k (2026-07-17) — register `notification_retention` sweep
-- work_type.
--
-- The sweep hard-deletes stale rows from tenant_notification and
-- notification_delivery_attempt per configurable retention rules.
-- Uses the DELETE grants added in schema_v75 (tenant_notification
-- and notification_delivery_attempt) — no schema-side change to
-- tables themselves; only the CHECK constraint on sweep_log needs
-- the new work_type value.

BEGIN;

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
        'notification_retention',
        'other'
    ]));

COMMIT;
