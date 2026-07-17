---
name: ship-3-prime-i-final-producers-2026-07-17
description: "Ship 3'.i — final two notification producers close the inventory at 13 kinds"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.i (2026-07-17) — closes the notification-producer arc.

## What shipped

Two producers + frontend polish:

### `posture_flip_to_comply` (write-path)

Mirror of Ship 3'.c's `nc_surfaced` in
`rag/intake/posture_writer.py::_log_status_change`. Fires when
`status_after == "Comply" and status_before != "Comply"`.
Severity `low` (positive news — auditor-neutral). Dedup via
partial unique index on `posture_id`.

Rationale: remediation success is worth surfacing so the tenant
can see the effect of a doc upload / manual review + the
notification serves as an audit trail. Doesn't require the
tenant to do anything.

### `api_key_expiring` (sweep-driven)

New `sweep_api_key_expiring` in `rag/scheduler/tick.py`.
Registered in `_WORK_TYPES` — fires on the 30-min systemd timer.

**Three escalating buckets**:
- `30d` → severity `medium` — plan the rotation
- `7d`  → severity `high`   — schedule the rotation
- `1d`  → severity `critical` — do the rotation NOW

Bucket label goes into `related_control_ref` so the partial
unique index dedupes per bucket: tenant gets three heads-up
across a key's final month, not a daily nag. `expires_at IS NULL`
(never expiring) and past-expiry keys are excluded.

`api_keys` already had:
- `expires_at` column (nullable)
- `app_all_api_keys` permissive policy for arioncomply_app

No schema change needed on `api_keys` itself.

### schema_v74

- Adds both kinds to `tenant_notification_kind_check` (13 kinds
  now).
- Adds `api_key_expiring` to `sweep_log_work_type_check`.
- No RLS grants needed (api_keys was already open for
  arioncomply_app; posture writer runs per-tenant).

### Frontend

- `_NOTIF_KIND_LABEL` extended with:
  - `posture_flip_to_comply` → "now compliant"
  - `api_key_expiring` → "API key expiring"
- `_NOTIF_KIND_META` extended with icons + destinations:
  - `posture_flip_to_comply` → `ti-mood-happy` + `dashboard`
  - `api_key_expiring` → `ti-key` + `profile`

## Tests

8 new source-read + capture tests in
`tests/test_notification_producers.py`:

- 4 `posture_flip_to_comply`: OFI→Comply fires + NC→Comply fires
  (remediation success) + Comply→Comply skips + Comply→OFI
  regression skips
- 4 `api_key_expiring`: wiring + severity buckets + dedup key +
  expiry-boundary guards (`IS NOT NULL` + `> NOW()`)

**28/28 passing** (was 20/20 in Ship 3'.g).

Smoke-tested end-to-end:
- 3 seeded api_keys (25d / 5d / 18h out) → 3 correctly-severed
  notifications (medium / high / critical); second sweep run
  dedup-verified (0 new)
- Direct call to `_log_status_change`: OFI→Comply fires with
  severity `low`; Comply→Comply skips

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1530_ship3i.csv`). Same #200 WARN as
prior baselines. Producer changes don't touch the RAG path.

## Producer inventory FINAL

13 kinds in `tenant_notification_kind_check`:

| Kind | Producer | Where |
|---|---|---|
| implication_overdue | cascade engine | write path (Ship 3'.a) |
| followup_overdue | cascade engine | write path |
| threshold_crossed | cascade engine | write path |
| cascade_blocked | cascade engine | write path |
| auto_resolved | cascade engine | write path |
| freshness_expiry | sweep | Ship 3'.b |
| nc_surfaced | write path | Ship 3'.c |
| upload_processed | write path | Ship 3'.c |
| stage2_proposal_ready | write path | Ship 3'.e |
| upload_failed | write path | Ship 3'.e |
| overdue_followups | sweep (backstop) | Ship 3'.f |
| cite_verification_overdue | sweep | Ship 3'.g |
| **posture_flip_to_comply** | write path | Ship 3'.i |
| **api_key_expiring** | sweep | Ship 3'.i |

**Notification producer arc complete.** Every relevant audit,
operational, and defensibility event has a producer. Remaining
work in the notification space is consumer-side (inbox UX,
delivery reliability) rather than producer capability.

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]]
- [[ship-3-prime-b-freshness-expiry-producer-2026-07-17]]
- [[ship-3-prime-c-notification-producers-2026-07-17]]
- [[ship-3-prime-d-channel-config-ui-2026-07-17]]
- [[ship-3-prime-e-notification-producers-2026-07-17]]
- [[ship-3-prime-f-overdue-followups-2026-07-17]]
- [[ship-3-prime-g-cite-verification-overdue-2026-07-17]]
- [[ship-3-prime-h-inbox-per-kind-rendering-2026-07-17]]
