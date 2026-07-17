-- schema_v75_ship3j_notification_delete_grants.sql
--
-- Ship 3'.j (2026-07-17) — grant DELETE on notification tables to
-- arioncomply_app.
--
-- Why: the integration test in tests/test_notification_delivery.py
-- needs to clean up a throwaway test tenant's rows after each
-- fixture run. arioncomply_app already has full SELECT/INSERT/UPDATE
-- + the `app_*_all` permissive policies (schema_v70 / v72 / v73)
-- but never had DELETE. `tenant_notification_channel` already had
-- DELETE granted in schema_v70 for the Ship 3'.d channel-config
-- UI; this fills the gap for the parent + child tables.
--
-- This also unblocks a future notification retention sweep — a
-- soft-delete or hard-delete pass on read+dismissed rows older
-- than N days can now run under the sweep tick's arioncomply_app
-- role without escalating privileges.
--
-- Safety: read/write access was already unrestricted cross-tenant
-- via the permissive `app_*_all` policies (USING (true)), so this
-- grant doesn't change the tenant-isolation posture — it just
-- completes CRUD parity with the other notification tables.

BEGIN;

GRANT DELETE ON tenant_notification          TO arioncomply_app;
GRANT DELETE ON notification_delivery_attempt TO arioncomply_app;

COMMIT;
