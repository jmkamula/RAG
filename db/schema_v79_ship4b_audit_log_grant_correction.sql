-- schema_v79_ship4b_audit_log_grant_correction.sql
--
-- Ship 4'.b addendum (2026-07-17) — correct the accumulated
-- inconsistency between "compliance-load-bearing audit trail"
-- and "diagnostic log" tables.
--
-- The Ship 3'.j audit ([[feedback-rls-grant-parity]]) treated 3
-- append-only log tables (ai_call_log, intake_trace_log,
-- posture_status_log) as immutable "audit logs, no DELETE by
-- design". Ship 4'.b's audit-log-FK teardown pain (see
-- [[feedback-test-fixture-audit-log-fks]]) prompted a re-read.
-- Honest evaluation of purpose:
--
--   Load-bearing compliance evidence (immutable, RESTRICT):
--     * posture_status_log — the audit trail of posture changes;
--       auditor evidence for "what was our stance on control X on
--       date Y?"
--
--   Diagnostic logs (not evidence artifacts; retention-eligible):
--     * ai_call_log        — LLM cost/latency tuning, prompt debug
--     * chat_casefile_log  — Ship 2' digest observability
--     * chat_consensus_log — Ship 1 consensus tuning
--     * intake_trace_log   — intake pipeline QA
--     * fact_recompute_log — Ship 3'.a fact-recompute observability
--
-- Two red flags found in the current state:
--
--   1. `ai_call_log` had UPDATE granted but NOT DELETE. That's
--      worse than DELETE for audit integrity — you can silently
--      rewrite a row's LLM metadata. Since this isn't actually an
--      evidence-integrity table, we're fixing both directions:
--      revoke UPDATE, grant DELETE. Diagnostic-log semantics only.
--
--   2. `posture_status_log` had `ON DELETE CASCADE` on its tenant
--      FK. Meaning: deleting a tenant would silently erase the
--      auditor-evidence trail of every posture change they ever
--      had. Backwards for a load-bearing table. Change to
--      RESTRICT — deletion of a tenant with posture history now
--      requires an explicit "erase" flow (future superuser
--      operation for GDPR Art.17 or offboarding).
--
-- The 5 diagnostic logs get DELETE grants + `app_*_all` permissive
-- policies (mirror of the notification-tables pattern from
-- schema_v70). A future `sweep_diagnostic_log_retention` sweep
-- can now run under arioncomply_app.

BEGIN;

-- ── 1. Grant DELETE + revoke UPDATE on ai_call_log ──────────────────
-- (UPDATE on an LLM-call log entry is a footgun; DELETE for
-- retention is the honest need.)
GRANT DELETE ON ai_call_log TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: Ship 4'.b diagnostic reclassification (retention-eligible).
REVOKE UPDATE ON ai_call_log FROM arioncomply_app;

-- ── 2. Grant DELETE on the 4 other diagnostic logs ──────────────────
-- Also enable RLS + a permissive `app_*_all` policy so cross-tenant
-- retention sweeps can iterate the way schema_v70 established.
GRANT DELETE ON chat_casefile_log  TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: Ship 4'.b diagnostic reclassification (retention-eligible).
GRANT DELETE ON chat_consensus_log TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: Ship 4'.b diagnostic reclassification (retention-eligible).
GRANT DELETE ON fact_recompute_log TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: Ship 4'.b diagnostic reclassification (retention-eligible).
GRANT DELETE ON intake_trace_log   TO arioncomply_app;  -- APPEND-ONLY-EXEMPT: Ship 4'.b diagnostic reclassification (retention-eligible).

-- Add permissive policies (idempotent — DROP + CREATE).
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT unnest(ARRAY[
        'ai_call_log',
        'chat_casefile_log',
        'chat_consensus_log',
        'fact_recompute_log',
        'intake_trace_log'
    ]) LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS app_%s_all ON %I', t, t);
        EXECUTE format($p$
            CREATE POLICY app_%1$s_all ON %1$I
                AS PERMISSIVE FOR ALL
                TO arioncomply_app
                USING (true) WITH CHECK (true)
        $p$, t);
    END LOOP;
END $$;

-- ── 3. Harden posture_status_log ────────────────────────────────────
-- Change the tenant FK from ON DELETE CASCADE → NO ACTION (RESTRICT
-- equivalent). Auditor-evidence trail must not silently disappear
-- when a tenant is deleted.
--
-- Tenant deletion involving posture history now REQUIRES an
-- explicit "erasure" operation — future work.
ALTER TABLE posture_status_log
    DROP CONSTRAINT IF EXISTS posture_status_log_tenant_id_fkey;

ALTER TABLE posture_status_log
    ADD CONSTRAINT posture_status_log_tenant_id_fkey
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);
    -- (Default is NO ACTION — blocks tenant DELETE while any log
    -- row references the tenant. Same semantics as RESTRICT.)

-- Confirm arioncomply_app has NO UPDATE / DELETE on
-- posture_status_log (it should already be INSERT/SELECT-only from
-- earlier schemas — this REVOKE is defensive):
REVOKE UPDATE, DELETE ON posture_status_log FROM arioncomply_app;

COMMENT ON TABLE posture_status_log IS
'Compliance-load-bearing audit trail of posture status changes. Append-only by contract for arioncomply_app (INSERT + SELECT only). Tenant FK is NO ACTION so tenant deletion requires explicit erasure flow. Do NOT grant UPDATE or DELETE without designing an erasure-with-provenance mechanism.';

COMMENT ON TABLE ai_call_log IS
'Diagnostic log for LLM call cost/latency/prompt debugging. NOT a compliance-evidence artifact — arioncomply_app has INSERT/SELECT/DELETE (retention-eligible), UPDATE explicitly revoked to prevent silent history rewrites.';

COMMENT ON TABLE chat_casefile_log IS
'Diagnostic log for Ship 2'' case-file digest observability. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';

COMMENT ON TABLE chat_consensus_log IS
'Diagnostic log for Ship 1 consensus tuning. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';

COMMENT ON TABLE fact_recompute_log IS
'Diagnostic log for Ship 3'' fact-recompute sweep observability. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';

COMMENT ON TABLE intake_trace_log IS
'Diagnostic log for intake-pipeline QA. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE.';

COMMIT;
