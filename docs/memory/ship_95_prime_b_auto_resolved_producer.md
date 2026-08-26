---
name: ship-95-prime-b-auto-resolved-producer
description: Ship 95'.b — wires the tenant_notification producer for kind='auto_resolved'. Kind existed in the schema_v70 allowlist since 2026-07 but no code path emitted it, so the retired "Auto-closed (7d)" retro tile had no alternative surface. Now every cascade-engine auto-closure lands in the tenant's Notifications inbox.
metadata:
  type: project
---

# Ship 95'.b — Auto-resolved producer wire (2026-08-26)

## Framing

Ship 95'.a retired the "Auto-closed (7d)" retro tile from the
Dashboard KPI strip. Two of the three retired tiles (Muted /
Verifications) had reachability on other existing surfaces
(Cascade timeline + Profile). But Auto-closed did not — the
`auto_resolved` notification kind was in the `schema_v70`
allowlist since 2026-07 but **no code path emitted it**. The
cascade engine's auto-close loop at `engine.py:1051` just
incremented an internal counter.

That made Ship 95'.a a **half-shipped retirement** — data that
was surfaced (however cluttered) went completely unreachable.

Ship 95'.b closes the gap with a single-purpose producer wire.

## Delivered

**`rag/cascade/engine.py`**:

- New module-level `logger = logging.getLogger(__name__)` — the
  module didn't have one; adding without a callsite would have
  been dead code, so this arc is when it earns its place.

- New `_emit_auto_resolved_notifications()` helper. Takes
  `(pg_cursor, tenant_id, req_id, event_type, impl_ids)` and
  emits one `kind='auto_resolved'` notification per closed
  implication:

  - `severity='low'` per `notify.py` convention ("auto-resolved
    confirmation (FYI)")
  - `title = "Follow-up closed for {ctrl_ref}"` using the tail
    control_ref, not the full requirement id (advisory-tone rule
    — no `ISO27001:2022:A.5.16` in tenant prose)
  - `body` explains what happened + says "no action needed"
  - `related_entity_kind='triggered_implication'` +
    `related_entity_id=<impl uuid>` — dedups via notify.py's
    partial unique index (kind + entity_id) so a re-run doesn't
    double-fire
  - Per-notify exception handling — engine's error path never
    triggers on inbox-write failures

- Call site at the tail of the auto-resolve `for req_id` loop.
  Captures the `RETURNING id` list from the UPDATE (was
  `len(pg_cursor.fetchall())` alone) → passes to the helper.

**`tests/test_notification_producers.py`** — 4 new tests
(32 → 32 all pass; existing tests unchanged):

- `test_auto_resolved_fires_one_per_impl_id` — 2 ids in →
  2 captured calls out, all expected fields (kind / severity /
  related_control_ref / related_event_type) present
- `test_auto_resolved_no_impl_ids_no_call` — empty list → no
  notify calls (the no-op case)
- `test_auto_resolved_control_ref_split_from_full_req_id` —
  body prose + related_control_ref use `A.5.16`, never
  `ISO27001:2022:A.5.16`
- `test_auto_resolved_survives_notify_exception` — monkey-
  patched notify raises → helper returns 0, no propagation

## Design notes

**Why extract a helper** — the auto-resolve block sits inside a
500-line `apply_verification()` function that walks Neo4j + emits
multiple table writes. Testing the notification emission inline
would require full engine setup with mocked Neo4j sessions.
Extracting the notify loop to a top-level helper `_emit_...()`
lets the test pass a fake cursor + a monkey-patched notify + zero
Neo4j scaffolding. The engine call site becomes a 6-line
delegate.

**Why one notification per implication** — a single verification
could auto-close 5 implications across 5 controls (e.g.
`personnel_offboarded` closing A.5.16 + A.5.17 + A.5.18). Rolling
up to a single notification would obscure per-control provenance
that auditor-visibility needs. Notify.py's partial unique index
already dedups repeat fires for the same (kind, entity_id) —
the "spam" concern is bounded at the entity level, not the
count level.

**Why severity 'low'** — this is a positive event; the tenant
doesn't need action. Ship 3'.h `notify.py` convention already
tags severity=low as "auto-resolved confirmation (FYI)". Consistent.

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved.

Producer unit tests: 32/32 pass (4 new).

## Codified lessons

**Lesson 124: Notification kinds without producers are ghost UX
contracts.** The `auto_resolved` kind sat in the CHECK constraint
allowlist for ~13 months without a producer. The schema said
"this kind can happen"; the code never made it happen. UI code
(inbox rendering, humanization, deep-links) may have already
handled it — a ghost contract. Rule: when adding a notification
kind to the allowlist, either wire the producer in the same PR or
add a `# TODO producer for kind=X` marker on the CHECK constraint
migration. Reviewing an isolated schema change can't reveal a
missing producer.

**Lesson 125: Half-shipped retirement is real.** Ship 95'.a
looked like a clean visual restructure — 5 tiles → 3, all
retro data preserved elsewhere. Almost true. One of three retros
had no alternative surface at all; without Ship 95'.b, the
Auto-closed retirement was pure data loss. Rule: a
retirement-with-preservation only holds when all N retired
surfaces have a proven-reachable home. Two-of-three preserved is
half-shipped. Codify this alongside Lesson 122 (retirement
without a reachability audit is data loss) — the audit checks
existence, but the ship check must verify each preserved surface
actually resurfaces the data.

**Lesson 126: Extract-then-test unlocks orchestrator-buried
code.** The auto-resolve notify emit was ~15 lines inside a
500-line function. Testing it inline would demand full engine
scaffolding (Neo4j session mock + structured events + all upstream
UPDATE targets). Extracting to a top-level `_emit_...()` helper —
same code, different module-level identifier — reduced the test
surface from "test the engine" to "test a small pure function"
with 4 tests + a monkey-patch. Rule: when a producer sits inside
an orchestrator that's expensive to test, the extraction cost
(6-line delegate in the orchestrator + module-level helper) is
almost always worth the test-coverage gain.

## Related

- [[ship-95-prime-a-dashboard-kpi-restructure]] — the arc this
  closes the reachability gap for
- [[ship-3-prime-h-notification-inbox]] — where the
  `auto_resolved` kind was added to the allowlist without a
  producer
- Ship 3'.f / 3'.g / 3'.i — other notification producers that
  DID land with their kinds (freshness_expiry / cite_verification
  _overdue / api_key_expiring). The pattern for producers that
  DIDN'T land is what Ship 95'.b codifies as a lesson.
- [[feedback-advisory-tone-not-authoritative]] — tenant-facing
  body prose (`{ctrl_ref}` not `ISO27001:2022:{ctrl_ref}`)
  follows this rule
