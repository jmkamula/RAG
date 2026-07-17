-- schema_v76_rls_grant_parity.sql
--
-- 2026-07-17 — RLS + GRANT parity fix (post-Ship 3'.j discussion).
--
-- Ship 3'.j surfaced a class of gap: tables where arioncomply_app has
-- a permissive `USING (true)` RLS policy that reads as "cross-tenant
-- access granted" but the SQL-standard GRANTs on those tables don't
-- include DELETE. Result: silent behavior — DELETE fails with
-- "permission denied" that a `try/except: pass` swallows without
-- signal.
--
-- Audit of tables with an arioncomply_app + `USING (true)` policy
-- returned 9 gaps. Of those:
--
--   Stay no-DELETE by design (audit / append-only logs):
--     ai_call_log         — LLM call trace
--     intake_trace_log    — no UPDATE either — append-only by design
--     posture_status_log  — no UPDATE either — append-only by design
--
--   Legitimate DELETE candidates (this patch):
--     api_keys                  — future key-management UI
--     expected_followup_event   — cascade cleanup / retention
--     triggered_implication     — cascade cleanup / retention
--     tenant_evidence_gaps      — advisory row cleanup
--     workbook_intake_proposal  — rejected-proposal cleanup
--     posture_assertions        — long-tail retention (supersession is
--                                  UPDATE today; DELETE is future work)
--
-- Not addressing today: no prod code path DELETEs from these tables.
-- This is a pre-emptive alignment so the NEXT developer who wires a
-- DELETE doesn't hit the same silent-failure trap. The `app_*_all`
-- policies already grant cross-tenant read/write via USING (true),
-- so this doesn't broaden the tenant-isolation posture — it just
-- completes CRUD parity where the intent is clearly "full app
-- access for maintenance".

BEGIN;

GRANT DELETE ON api_keys                 TO arioncomply_app;
GRANT DELETE ON expected_followup_event  TO arioncomply_app;
GRANT DELETE ON triggered_implication    TO arioncomply_app;
GRANT DELETE ON tenant_evidence_gaps     TO arioncomply_app;
GRANT DELETE ON workbook_intake_proposal TO arioncomply_app;
GRANT DELETE ON posture_assertions       TO arioncomply_app;

COMMIT;
