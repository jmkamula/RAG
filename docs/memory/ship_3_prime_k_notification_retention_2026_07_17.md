---
name: ship-3-prime-k-notification-retention-2026-07-17
description: "Ship 3'.k — notification retention sweep closes the unbounded-inbox gap"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.k (2026-07-17) — final scheduled cleanup pass for the
notification pipeline.

## Problem

Ships 3'.a-j landed a fully functional pipeline: 13 producers,
delivery worker, inbox UI, sweep scheduler. But the pipeline
had no age-out mechanism — `tenant_notification` +
`notification_delivery_attempt` were designed to grow
unboundedly. A tenant running for a year with even modest
sweep activity would accumulate thousands of read+dismissed
rows the tenant no longer cares about.

## What shipped

### `sweep_notification_retention` in `rag/scheduler/tick.py`

Hard-deletes stale rows per configurable thresholds:

| Rule | Threshold | Meaning |
|---|---|---|
| (a) `dismissed_at + fired_at < NOW - 30d`  | 30d  | Tenant explicitly said "go away" — quickest cleanup |
| (b) `read_at + fired_at < NOW - 90d`       | 90d  | Tenant saw + acknowledged, keep as history for a quarter |
| (c) `fired_at < NOW - 365d` (any state)    | 365d | Hard ceiling — after a year, even unread ages out |
| Attempts | `attempted_at < NOW - 90d`  | 90d  | Delivery audit trail retention |

Conservative defaults — favour keeping data over deleting it.
Constants at module-scope for easy tuning
(`_RETENTION_DISMISSED_DAYS` / `_RETENTION_READ_DAYS` /
`_RETENTION_MAX_AGE_DAYS` / `_RETENTION_ATTEMPT_DAYS`).

Registered as `notification_retention` work_type; fires on the
30-min systemd timer alongside the other sweeps. Attempt
cleanup happens BEFORE notification cleanup so the sweep_log
row reads chronologically for auditors.

No FK enforcement between `notification_delivery_attempt` and
`tenant_notification` — attempts orphaned by rule (c) age out
independently on their own 90d clock.

### `db/schema_v77_ship3k_retention_work_type.sql`

Adds `notification_retention` to `sweep_log_work_type_check`.
No table changes — the DELETE grants from Ship 3'.j's
schema_v75 already covered what this sweep needs.

## Tests

`tests/test_notification_retention.py` — 7 integration tests,
same fixture pattern as `test_notification_delivery.py`
(throwaway test tenant UUID `88888888...`, cleanup on exit).
Coverage:

1. All 3 delete rules → correct rows deleted, 2 keep rows survive
2. Dismissed rule uses shorter window (20d dismissed survives)
3. Read-not-dismissed uses 90d window (60d read survives)
4. Max-age ceiling applies regardless of state (unread 400d deleted)
5. Attempt aging independent (100d attempt deleted, 10d attempt kept)
6. Dry-run deletes nothing (count-only report)
7. `sweep_log` row written with `completed` status + counts

**7/7 passing.** Zero test residue.

## Full test suite status

- `tests/test_notification_producers.py` — 28/28
- `tests/test_notification_delivery.py` — 7/7
- `tests/test_notification_retention.py` — 7/7 (new)
- **42/42 total** across the notification arc

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1724_ship3k.csv`). Same #200 WARN.
No RAG path change; regression guard only.

## Notification arc — TRULY COMPLETE

- 13 producers (Ships 3'.a-i)
- Delivery worker validated (Ship 3'.j)
- Retention sweep landed (Ship 3'.k)
- Inbox UI with per-kind deep-links (Ships 3'.h+i)
- Sweep scheduler productionized via systemd (Ship 3'.a)
- RLS + GRANT parity swept (schema_v76 patch)

Sweep tick now runs 7 work_types every 30 minutes:
`fact_recompute`, `overdue_followups`, `freshness_expiry`,
`cite_verification_overdue`, `api_key_expiring`,
`notification_delivery`, **`notification_retention`**.

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]] — where the sweep scheduler landed
- [[ship-3-prime-j-delivery-integration-tests-2026-07-17]] — established the integration-test pattern this arc extends
- [[feedback-rls-grant-parity]] — the discipline this arc benefits from
