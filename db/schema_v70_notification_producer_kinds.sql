-- schema_v70_notification_producer_kinds.sql
--
-- Ship 3'.c (2026-07-17) — expand tenant_notification.kind to cover
-- two new producers wired in this arc.
--
-- Adds:
--   nc_surfaced        — a control's live posture finding transitioned
--                        to NC (from any non-NC state).
--   upload_processed   — a document upload's Stage-1 extraction
--                        completed, with a summary of findings.
--
-- The existing kinds (implication_overdue, followup_overdue,
-- threshold_crossed, cascade_blocked, auto_resolved, freshness_expiry)
-- stay untouched.

BEGIN;

-- Drop both legacy names so this is idempotent regardless of history.
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
        'freshness_expiry',
        'nc_surfaced',
        'upload_processed'
    ]));

COMMENT ON COLUMN tenant_notification.kind IS
'Notification category. Kinds added in Ship 3''.c (2026-07-17): nc_surfaced (live posture flipped to NC — fired at write time by rag/intake/posture_writer.py::_log_status_change); upload_processed (Stage-1 extraction completed — fired at write_findings() return).';

COMMIT;
