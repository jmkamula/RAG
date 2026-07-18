---
name: feedback-rls-grant-parity
description: "RLS `USING (true)` policies don't imply matching SQL GRANTs — audit both when giving arioncomply_app cross-tenant maintenance access"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When adding a permissive `app_*_all ... USING (true)` policy for
`arioncomply_app` (the pattern shipped in schema_v70/v72/v73 for
cross-tenant maintenance sweeps), ALSO grant the matching CRUD
privileges. RLS policies and SQL GRANTs are two independent
layers — policies say WHAT rows are visible, GRANTs say WHAT
operations are allowed.

**Why:** Ship 3'.j's integration test cleanup failed silently
because `tenant_notification` had `app_notification_all USING
(true)` but no DELETE grant. The DELETE raised `permission
denied` that the fixture's `try/except: pass` swallowed. Six
more tables had the same latent gap (audited via `pg_policies`
JOIN `information_schema.table_privileges`).

**How to apply:**

- Any new `CREATE POLICY app_X_all ... USING (true)` on a table
  should be followed in the same migration by
  `GRANT SELECT, INSERT, UPDATE, DELETE ON X TO arioncomply_app`,
  unless the table is:
  * **compliance-load-bearing evidence** (`posture_status_log`
    — the audit trail of posture changes; auditor-required
    evidence for control history). Leave UPDATE + DELETE off
    by design. See schema_v79 hardening.
  * a case where least-privilege genuinely matters (rare — the
    permissive policy already gave read/write to everything)

- **Diagnostic logs are NOT audit logs.** Ship 4'.b's addendum
  (schema_v79) corrected an earlier misclassification: 5 tables
  I had labeled "audit logs" (`ai_call_log`, `chat_casefile_log`,
  `chat_consensus_log`, `fact_recompute_log`, `intake_trace_log`)
  are just diagnostic logs — LLM cost/latency tuning, digest
  observability, pipeline QA. They're retention-eligible and now
  have DELETE grants + permissive policies. Only `posture_status_log`
  is genuinely load-bearing.
- Also from schema_v79: `ai_call_log` had UPDATE granted but not
  DELETE — worse than DELETE for integrity (silent history
  rewrites). Now: `INSERT/SELECT/DELETE` only.
- Reversal check when auditing: query tables that have the
  `app_*_all` policy pattern and ensure GRANTs align:

```sql
SELECT p.tablename,
       string_agg(t.privilege_type, ',' ORDER BY t.privilege_type) AS privs
  FROM pg_policies p
  LEFT JOIN information_schema.table_privileges t
    ON t.table_name = p.tablename
   AND t.grantee    = 'arioncomply_app'
 WHERE 'arioncomply_app' = ANY (p.roles)
   AND p.permissive = 'PERMISSIVE'
   AND p.qual = 'true'
 GROUP BY p.tablename
 ORDER BY p.tablename;
```

- schema_v76 (2026-07-17) aligned the 6 legitimate DELETE
  candidates. **schema_v79 (Ship 4'.b addendum) corrected the
  earlier "3 audit logs stay no-DELETE" claim** — 5 tables
  reclassified from "audit" to "diagnostic" (DELETE granted,
  retention-eligible). Only `posture_status_log` remains
  genuinely load-bearing (INSERT/SELECT only + tenant FK
  hardened from CASCADE to NO ACTION).

Related: [[ship-3-prime-j-delivery-integration-tests-2026-07-17]]
(where the gap surfaced),
[[ship-3-prime-d-channel-config-ui-2026-07-17]] (where the
`app_*_all` policy pattern was established),
[[ship-4-prime-b-audit-log-correction-2026-07-17]] (Ship 4'.b
addendum that corrected the classification).
