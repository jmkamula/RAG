---
name: ship-4-prime-b-audit-log-correction-2026-07-17
description: "Ship 4'.b addendum — correct the diagnostic-vs-audit-log misclassification carried since Ship 3'.j"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.b addendum (2026-07-17) — schema-only correction that
fixes an inconsistency the notification arc accumulated.

## The trigger

Ship 4'.b's test fixture couldn't cleanly delete its test tenant
because 5 tables blocked the FK cascade. I initially called them
"append-only audit logs by design" and wrote around the problem
(see [[feedback-test-fixture-audit-log-fks]]).

The user pushed back: "can we dig deeper into the audit-log
tables block". The audit surfaced two red flags:

1. **`ai_call_log` had UPDATE granted but not DELETE.** Rewriting
   a row's LLM metadata silently is worse than deleting it.
2. **`posture_status_log` had `ON DELETE CASCADE` on its tenant
   FK.** Meaning: the ONE table that's arguably load-bearing for
   compliance evidence (audit trail of posture changes) would
   silently disappear on tenant deletion, while pure diagnostic
   logs blocked it. Backwards priority.

## The distinction (finally named)

- **Compliance-load-bearing audit trail** — auditor-required
  evidence of what state a control was in over time. Must be
  immutable + retention-untouched by the app.
  * `posture_status_log`

- **Diagnostic logs** — cost/latency/debug telemetry, not
  evidence artifacts. Retention-eligible; can be pruned by a
  sweep.
  * `ai_call_log` — LLM cost/latency/prompt debug
  * `chat_casefile_log` — Ship 2' digest observability
  * `chat_consensus_log` — Ship 1 consensus tuning
  * `fact_recompute_log` — Ship 3'.a sweep observability
  * `intake_trace_log` — intake pipeline QA

## What shipped

### `db/schema_v79_ship4b_audit_log_grant_correction.sql`

Diagnostic logs (5 tables):
- Grant DELETE to arioncomply_app
- Revoke UPDATE on ai_call_log (defense against silent history
  rewrites)
- Enable RLS + add permissive `app_*_all` policy (mirror of
  schema_v70 pattern)
- Add COMMENT explaining classification + retention-eligibility

Compliance-load-bearing (posture_status_log):
- FK from tenant_id changed from `ON DELETE CASCADE` → no ON
  DELETE clause (default NO ACTION = RESTRICT semantics).
  Tenant deletion involving posture history now REQUIRES an
  explicit erasure operation.
- Revoke UPDATE/DELETE (defensive — should already be
  INSERT/SELECT only)
- Add COMMENT explaining the "do NOT grant UPDATE or DELETE
  without designing an erasure-with-provenance mechanism"
  invariant

### Updated feedback memory

[[feedback-rls-grant-parity]] rewritten to reflect the new
classification and cross-reference this schema.

## Verify state (post-fix)

    ai_call_log        | DELETE,INSERT,SELECT           | plain FK (RESTRICT)
    chat_casefile_log  | DELETE,INSERT,SELECT           | plain FK
    chat_consensus_log | DELETE,INSERT,SELECT           | plain FK
    fact_recompute_log | DELETE,INSERT,SELECT           | plain FK
    intake_trace_log   | DELETE,INSERT,SELECT           | plain FK
    posture_status_log | INSERT,SELECT                  | plain FK (was CASCADE — HARDENED)

Six tables, one truly append-only, five diagnostic.

## What this unblocks (future work)

- Retention sweep for diagnostic logs — a `sweep_diagnostic_
  log_retention` work_type analogous to Ship 3'.k
  `notification_retention`. Cadence + thresholds TBD; these
  tables will grow much faster than notifications.
- GDPR right-to-erasure / tenant offboarding — need to design
  a superuser-triggered "erase" flow that:
  1. Marks the tenant deleted
  2. Deletes tenant-owned data (evidence, uploads, posture)
  3. Handles posture_status_log with signed provenance
     (hashed export? external archive?) rather than blind
     DELETE — because RESTRICT will block naive tenant
     deletion for any tenant with posture history

## Baseline

External API test suite: 13/13 still pass with corrected
grants. Full eval: running (expected 207/208).

## Note on Ship 4'.b's fixture

[[feedback-test-fixture-audit-log-fks]] documented the "leave
tenant + user idempotent" pattern I used before understanding
the misclassification. With schema_v79 applied, the fixture
COULD do full tenant DELETE for tenants that never wrote to
posture_status_log — the 5 diagnostic logs no longer block.
But the pattern is still fine as-is: idempotent seed +
surgical key delete = zero test residue, no DB drift.
Kept the fixture; updated the memory to reflect the corrected
model.

## Related

- [[ship-4-prime-b-query-endpoint-2026-07-17]] — the arc where
  the fixture pain surfaced
- [[feedback-rls-grant-parity]] — the parent principle,
  updated in this arc
- [[feedback-test-fixture-audit-log-fks]] — the fixture pattern
  that emerged from the pre-correction understanding
