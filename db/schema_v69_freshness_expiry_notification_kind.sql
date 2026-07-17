-- schema_v69_freshness_expiry_notification_kind.sql
--
-- Ship 3'.b (2026-07-17) — add 'freshness_expiry' to the
-- tenant_notification.kind CHECK constraint.
--
-- Ship 3'.a productionized the scheduler tick with a stub
-- `sweep_freshness_expiry`. This migration is a prerequisite for
-- filling in the stub: the sweep needs to write tenant_notification
-- rows tagged with a new kind so the UI can filter them separately
-- from cascade-family kinds.
--
-- Idempotent: drops and re-adds the CHECK constraint.

BEGIN;

-- Drop BOTH possible legacy constraint names (the original migration
-- didn't name it consistently).
ALTER TABLE tenant_notification
    DROP CONSTRAINT IF EXISTS tenant_notification_kind_chk;
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
        'freshness_expiry'
    ]));

COMMENT ON COLUMN tenant_notification.kind IS
'Notification category. freshness_expiry (added Ship 3''.b, 2026-07-17): a Comply posture is past its EvidenceRequirement freshness_days window. Fired by the periodic sweep tick.';

COMMIT;
