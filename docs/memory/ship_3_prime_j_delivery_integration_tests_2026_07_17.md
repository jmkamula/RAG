---
name: ship-3-prime-j-delivery-integration-tests-2026-07-17
description: "Ship 3'.j — end-to-end integration tests for the notification delivery worker + DELETE grants that also unblock a future retention sweep"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.j (2026-07-17) — validates the last mile of the
notification pipeline.

## Problem

Ships 3'.a-i built the producer side of the pipeline (13 kinds +
sweep scheduler + inbox UI). The DELIVERY worker in
`rag/notifications/deliver.py` was written in Ship 3'.a but
never exercised end-to-end. SMTP + Slack code paths, severity
gate, dedup, retry-on-failure — all unproven against a real DB.

## What shipped

### `tests/test_notification_delivery.py` — first integration test in the repo

7 tests, all against a **throwaway test tenant** (UUID
`99999999-9999-9999-9999-999999999999`) so no interference with
the eval-covered Arion tenant.

Fixture context manager seeds:
- 1 tenant row (idempotent ON CONFLICT)
- 1 email channel (`min_severity='medium'`)
- 1 slack channel (`min_severity='high'`)
- 1 medium-severity notification

Teardown deletes all seeded rows.

SMTP + Slack are monkey-patched via `smtplib.SMTP` +
`urllib.request.urlopen` replacements. The patches also flip the
module-level bindings in `rag.notifications.deliver` (both
`_dm.smtplib.SMTP` and `_dm.urllib.request.urlopen`), so no
actual network I/O.

**Test coverage:**
1. `test_email_happy_path` — medium notif hits email (severity
   gate skips slack)
2. `test_slack_happy_path_with_high_severity` — critical
   notif reaches both channels
3. `test_severity_gate_skips_below_channel_floor` — DB confirms
   only 1 attempt row (no failed slack attempt logged)
4. `test_dedup_no_reattempt_after_success` — 2nd run of
   deliver_all skips already-delivered pairs via
   `_already_delivered()`
5. `test_retry_after_failure_lands_success` — SMTP raises →
   error row logged → SMTP fixed → success row logged
6. `test_dry_run_writes_no_attempts` — dry_run=True commits
   no delivery attempt rows
7. `test_give_up_boundary_filters_old_notifications` — notifications
   past `_GIVE_UP_DAYS` (7d) are filtered by
   `_undelivered_notifications` and never attempted

### `db/schema_v75_ship3j_notification_delete_grants.sql`

`arioncomply_app` had SELECT/INSERT/UPDATE on `tenant_notification`
+ `notification_delivery_attempt` but NOT DELETE — so test
fixture cleanup silently failed (`except Exception: pass` in
the finally block swallowed the permission-denied error). Grant
DELETE on both tables.

Safety: the permissive `app_*_all` policies (schema_v70) already
gave arioncomply_app cross-tenant read/write access via
`USING (true)`, so this grant doesn't change the tenant-isolation
posture — it just completes CRUD parity with
`tenant_notification_channel` (which had DELETE granted in v70
for the Ship 3'.d channel-config UI).

This also unblocks a future notification retention sweep — a
soft-delete or hard-delete pass on read+dismissed rows older
than N days can now run under arioncomply_app in the sweep tick.

## Debugging story

First test-run had 6/7 pass — `test_email_happy_path` failed
with `delivered=2` (should be 1). Root cause: a prior partial
run had committed seed rows but couldn't cleanup because
arioncomply_app lacked DELETE. The residue polluted the second
run's channel count. Fix: apply schema_v75 + manual cleanup +
rerun → 7/7 pass. Zero test residue post-run.

**Lesson**: integration tests need explicit privilege audits
before shipping. arioncomply_app's "app_*_all" policies read as
"unrestricted access" but they only cover WHAT the policy
covers — GRANTs are a separate layer. Both must align.

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1626_ship3j.csv`). Same #200 WARN.
Ship 3'.j doesn't touch the RAG path — pure additive:
delivery tests + DELETE grants.

## Notification pipeline status FINAL

- 13 producer kinds wired (Ships 3'.a-i)
- Delivery worker validated end-to-end (Ship 3'.j)
- Inbox UI complete with per-kind rendering + deep-links (Ship 3'.h+i)
- Sweep scheduler productionized via systemd timer (Ship 3'.a)

**The notification arc is complete.** Remaining work:
- Notification retention sweep (soft-delete read+dismissed rows
  older than N days) — schema_v75 already grants the DELETE
  needed for this
- Inbox per-row focus (Ship 3'.h deferred) — cross-cuts 4 loader
  functions on the frontend

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]] — where deliver.py landed
- [[ship-3-prime-d-channel-config-ui-2026-07-17]] — RLS pattern this arc follows
- [[ship-3-prime-i-final-producers-2026-07-17]] — producer arc completion
