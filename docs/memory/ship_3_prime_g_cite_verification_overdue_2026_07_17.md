---
name: ship-3-prime-g-cite-verification-overdue-2026-07-17
description: "Ship 3'.g — cite_verification_overdue sweep producer. Auditor-critical backstop for cite-mode."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.g (2026-07-17) — closes the biggest defensibility gap in
cite-mode. The `external_evidence_source` table tracks per-cite
verification cadence (`cadence_days` + `next_review_due`), but
nothing was actually enforcing the cadence.

## Problem

A tenant claims "Okta manages our access rights (see Okta admin
console)" via an `external_evidence_source` row. That claim is
only defensible if the tenant re-verifies the cite on cadence
(a `external_evidence_verification_log` entry that bumps
`last_verified_at` + `next_review_due` forward). Without
enforcement, a stale cite is worse than stale stored evidence —
there's no artefact in-product at all for the sample review to
fall back on.

## What shipped

- **`db/schema_v73_ship3g_cite_verification_overdue.sql`**:
  * Adds `cite_verification_overdue` to
    `tenant_notification.kind` CHECK (constraint now 11 kinds).
  * Adds `cite_verification_overdue` to `sweep_log.work_type`
    CHECK.
  * Adds permissive `app_external_evidence_source_all` RLS
    policy on `external_evidence_source` for `arioncomply_app`
    (same pattern as schema_v70 + v72).

- **`rag/scheduler/tick.py::sweep_cite_verification_overdue`**:
  Per-tenant sweep pattern (mirror of `sweep_freshness_expiry`):
  * SELECT active sources past `next_review_due`
  * Per-tenant loop with `set_config('app.tenant_id',...)`
  * Dedup: 7-day window SELECT + partial unique index (belt +
    braces — the SELECT catches dismissed-within-7-days re-fires
    that the partial index misses).

- **Severity ladder** — cite verification skews harder than
  freshness_expiry because there's no in-product artefact:
  * `last_verified_at IS NULL` (never verified) → `critical`
  * `staleness_ratio > 1.0` (past due by more than 1 cadence
    period) → `critical`
  * `staleness_ratio ∈ (0, 1.0]` → `high`

  Rationale: freshness_expiry lets stored evidence downgrade to
  `medium` at ≤1.5× because auditors can still sample the
  stored artefact and confirm the tenant knows about the
  staleness. Cite-mode has NO local artefact — auditor asks
  "when was this last verified?" and the tenant has no answer
  ≥ high.

- **Registration**: `_WORK_TYPES` dict + tick runner. Fires on
  the 30-min systemd timer alongside the other sweeps.

## Tests

5 new source-read tests in `tests/test_notification_producers.py`
(20/20 total). Also smoke-tested end-to-end:
- Seeded 1 never-verified + 1 verified-but-past-due (0.67 ratio)
- Sweep fired 2 notifications with correct severity split:
  never → critical, 0.67× → high
- Second sweep run confirmed dedup (0 fresh notifications)

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1413_ship3g.csv`). Same #200 WARN
(pre-existing gap_analysis/posture_check type-mismatch arc).

Ship 3'.g doesn't touch the RAG path — new sweep + schema + tests
only — so the eval was purely a regression guard.

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]]
- [[ship-3-prime-b-freshness-expiry-producer-2026-07-17]]
- [[ship-3-prime-c-notification-producers-2026-07-17]]
- [[ship-3-prime-d-channel-config-ui-2026-07-17]]
- [[ship-3-prime-e-notification-producers-2026-07-17]]
- [[ship-3-prime-f-overdue-followups-2026-07-17]]
- [[product-principle-evidence-stored-vs-cited]] — the cite/store model this sweep defends

## Producer inventory post Ship 3'.g

`tenant_notification_kind_check` now covers 11 kinds. Two producer
candidates remain from the survey:

- `posture_flip_to_comply` — mirror of Ship 3'.c's `nc_surfaced`
  (positive-news notifications; near-zero cost)
- `api_key_expiring` — operational hygiene (needs `expires_at`
  column on `api_keys` + sweep lane)

Everything auditor-critical is now wired. Remaining candidates
are UX/hygiene improvements rather than defensibility gaps.
