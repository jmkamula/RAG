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

-- Ship 3'.d also needs DELETE on tenant_notification_channel — the
-- frontend UI shipped in this arc lets tenants remove channels. The
-- table was created in schema_v66 which granted SELECT/INSERT/UPDATE
-- but not DELETE. Add it here (idempotent).
GRANT DELETE ON tenant_notification_channel TO arioncomply_app;

-- Ship 3'.d: cross-tenant maintenance access for the notification
-- delivery worker. Same pattern as posture_controls' app_posture_all
-- policy — the sweep tick reads across all tenants to iterate
-- undelivered notifications, so a tenant-scoped RLS blocks it.
-- Adding a permissive app policy (in addition to tenant_isolation)
-- lets arioncomply_app see all rows. Tenant callers (chat + UI) still
-- get scoped by tenant_isolation via set_config('app.tenant_id',...).
DROP POLICY IF EXISTS app_notification_all ON tenant_notification;
CREATE POLICY app_notification_all ON tenant_notification
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS app_notification_channel_all ON tenant_notification_channel;
CREATE POLICY app_notification_channel_all ON tenant_notification_channel
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS app_delivery_attempt_all ON notification_delivery_attempt;
CREATE POLICY app_delivery_attempt_all ON notification_delivery_attempt
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

COMMIT;
