---
name: ship-3-prime-f-overdue-followups-2026-07-17
description: "Ship 3'.f — real overdue_followups sweep producer replacing the counting stub; backstop for cascade write-path notify"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.f (2026-07-17) — productionized `overdue_followups` sweep.

## Problem

The `overdue_followups` work_type in `rag/scheduler/tick.py` was
a counting stub that queried a table (`cascade_events`) that
doesn't exist in this schema. Meanwhile the actual cascade
follow-up tracking lives in two tables:

- **`expected_followup_event`** — expected downstream events with
  `expires_at`; when past due, `status` should flip 'pending' →
  'overdue' + a `followup_overdue` notification fires.
- **`triggered_implication`** — cascade implications with
  `due_date` and `status='pending'`; when past due, an
  `implication_overdue` notification fires (no status flip —
  the table's CHECK doesn't have an 'overdue' status).

Both are already fired inline by the cascade engine's write path:
- `rag/cascade/engine.py:1085` — expected_followup_event
- `rag/cascade/posture_overlay.py:205` — triggered_implication

But those only run when another verification write triggers
reprocessing. If nothing writes after the deadline passes,
nothing fires. The sweep is the backstop.

## What shipped

- **`db/schema_v72_ship3f_cascade_app_policies.sql`** — permissive
  `app_expected_followup_all` + `app_triggered_implication_all`
  RLS policies for `arioncomply_app` on both cascade tables.
  Same pattern as schema_v70 for tenant_notification. Without
  this, the sweep sees 0 rows (RLS filters out everything).

- **`sweep_overdue_followups`** — real per-tenant sweep in
  `rag/scheduler/tick.py`. Two steps:

  1. Cross-tenant SELECT of pending overdue rows (both tables).
  2. Per-tenant loop with `set_config('app.tenant_id',...)`
     — UPDATE expected_followup_event to 'overdue' + `_notify()`
     for both classes.

- Dedup: `related_entity_id` = source row id (`fid` or `impl_id`);
  the partial unique index on `tenant_notification` kills dupes
  without a manual SELECT-then-INSERT guard.

- Severity ladder:
  * `expected_followup_event` — always `high`
  * `triggered_implication` — `critical` at cascade_depth ≤ 1
    (parent SLA slipping); `high` at depth ≥ 2 (derivative).

## Race handling

The UPDATE-then-RETURNING pattern for expected_followup_event
guards against the write path racing with the sweep — if
engine.py:1085 already flipped the row, our UPDATE finds no
match and we skip the notify. For triggered_implication (no
status flip), the partial unique index does the same job.

## Tests

5 new source-read tests in `tests/test_notification_producers.py`:
1. both kinds wired
2. expected_followup_event flip pattern (mirror of engine.py)
3. severity by cascade_depth
4. `dry_run` short-circuits before writes
5. `related_entity_id` dedup keys present

**15/15 passing.** Also smoke-tested end-to-end: seeded 1
expected_followup + 1 triggered_implication both past-due; sweep
notified 2/2 with correct severity + kind; second sweep run
notified 0 (dedup verified).

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1342_ship3f.csv`). Same #200 WARN
(pre-existing gap_analysis/posture_check type-mismatch arc,
unrelated).

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]]
- [[ship-3-prime-b-freshness-expiry-producer-2026-07-17]]
- [[ship-3-prime-c-notification-producers-2026-07-17]]
- [[ship-3-prime-d-channel-config-ui-2026-07-17]]
- [[ship-3-prime-e-notification-producers-2026-07-17]]

## What's left of the notification-producer arc

Three candidates remain from the Ship 3'.e survey:

- **`cite_verification_overdue`** — cite-mode
  `external_evidence_source.next_verification_due` past-due.
  Needs new sweep-tick lane + new kind (schema_v73).
  Highest auditor value.
- **`posture_flip_to_comply`** — mirror of Ship 3'.c's
  `nc_surfaced` in `_log_status_change`. Near-zero cost,
  positive-news notifications.
- **`api_key_expiring`** — operational hygiene. Needs
  `expires_at` column on `api_keys` + sweep lane. Doesn't
  matter for demo/eval work.
