-- schema_v108_cite_attestation_retention_sweep.sql
--
-- Ship 93'.z.i (2026-08-24) — retention sweep for cite_attestation_prompt.
--
-- Ship 92'.b's schema_v105 set expires_at DEFAULT NOW() + 30 days on the
-- prompt table but never wired an auto-expire path. This migration adds:
--
--   1. sweep_log.work_type += 'cite_attestation_retention'
--   2. Cross-tenant read policy on cite_attestation_prompt for
--      arioncomply_app so the sweep can enumerate expired rows across
--      tenants before setting per-tenant GUC + updating.
--
-- The sweep function itself is `rag/scheduler/tick.py::
-- sweep_cite_attestation_retention`.

BEGIN;

-- 1. sweep_log allowlist
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
        'risk_register_notify',
        'posture_refresh',
        'cite_attestation_retention',   -- Ship 93'.z.i (2026-08-24)
        'other'
    ]));

-- 2. Cross-tenant read policy for the sweep — mirror of the pattern
-- used for tenant_notification (schema_v70) and expected_followup_event
-- (schema_v72). arioncomply_app gets USING (true) so the sweep can
-- enumerate all expired rows; writes still go through the per-tenant
-- policy after set_config('app.tenant_id', ...).
DROP POLICY IF EXISTS app_cite_attestation_prompt_all ON cite_attestation_prompt;
CREATE POLICY app_cite_attestation_prompt_all ON cite_attestation_prompt
    AS PERMISSIVE FOR ALL
    TO arioncomply_app
    USING (true) WITH CHECK (true);

COMMIT;
