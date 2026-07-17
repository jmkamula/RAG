-- schema_v72_ship3f_cascade_app_policies.sql
--
-- Ship 3'.f (2026-07-17) — cross-tenant maintenance access for the
-- `overdue_followups` sweep in rag/scheduler/tick.py.
--
-- Same pattern as schema_v70 for tenant_notification, and
-- posture_controls' pre-existing app_posture_all policy:
-- arioncomply_app needs an `USING (true)` permissive policy to
-- iterate rows across all tenants for maintenance work. Tenant
-- callers (chat + UI) still get scoped by the existing
-- tenant_isolation policy via set_config('app.tenant_id',...).
--
-- Tables covered: expected_followup_event, triggered_implication.

BEGIN;

DROP POLICY IF EXISTS app_expected_followup_all ON expected_followup_event;
CREATE POLICY app_expected_followup_all ON expected_followup_event
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS app_triggered_implication_all ON triggered_implication;
CREATE POLICY app_triggered_implication_all ON triggered_implication
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

COMMIT;
