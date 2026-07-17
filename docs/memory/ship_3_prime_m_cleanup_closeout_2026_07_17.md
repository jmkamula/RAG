---
name: ship-3-prime-m-cleanup-closeout-2026-07-17
description: "Ship 3'.m — final cleanup sub-arc closing Ship 3' with inbox per-row focus + docstring hygiene"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.m (2026-07-17) — Ship 3' arc close-out.

## Scope

Three small cleanup items to close the arc:

1. **Inbox per-row focus** — Ship 3'.h's deferred UX. Deep-links
   now scroll+flash the target row on landing, not just the
   destination mode.
2. **tick.py docstring cleanup** — header still described
   `overdue_followups` and `freshness_expiry` as "stub"; both
   became real in Ships 3'.b + 3'.f.
3. **Ship 3' arc retrospective memory** — full-arc synthesis.

## What shipped

### Inbox per-row focus (`static/arioncomply.html`)

Two-layer pattern:

- **Producer**: `_notifOpen(id, kind, ref, entity_id)` extended
  to stash `window._notifTarget = {kind, ref, entity_id}` before
  `setMode(target)`. Button in `renderInbox` passes the
  notification's `related_control_ref` + `related_entity_id`.

- **Consumer**: shared helper `_applyNotifFocus()` called at the
  end of each target loader's render pass. Finds the matching
  row via `[data-focus-entity="uuid"]` (preferred) or
  `[data-focus-ref="A.5.18"]` selector, scrolls it into view,
  applies a temporary `.notif-focus-flash` class (2.2s
  purple-to-transparent animation), then clears
  `window._notifTarget` so a subsequent mode switch doesn't
  re-flash.

**Loaders taught**:
- Dashboard heatmap — `data-focus-ref` on `.heat-cell` (already
  had `data-ref`, added `data-focus-ref` alongside)
- Queue Stage-1 — `data-focus-ref` on `.qcard`
- Queue Stage-2 — `data-focus-ref` on `.qcard`
- Cascade timeline — `data-focus-entity="event_id"` + optional
  `data-focus-ref="control_ref"` on each row div

**Loaders NOT taught** (follow-up scope):
- Docs mode — upload rows need `data-focus-entity="upload_id"`
  but the upload-listing render wasn't inspected. `upload_failed`
  + `upload_processed` deep-links still land tenants on the
  Docs mode, just without per-row focus.
- Profile mode — `api_key_expiring` deep-links land here but
  API-key rows would need `data-focus-entity` too.

Scope decision: cover the majority of deep-link kinds cleanly
without a full loader refactor. The 4 taught loaders cover
9 of the 13 notification kinds' primary destinations.

### tick.py docstring cleanup

Header lines 25-29 no longer describe `overdue_followups` +
`freshness_expiry` as stubs. Replaced with real per-work-type
descriptions covering all 7 sweep kinds + their Ship-arc
references (3'.b/f/g/i/k). Docs now match code.

### Ship 3' arc retrospective

New memory entry [[ship-3-prime-arc-retrospective-2026-07-17]]
captures:
- 13-sub-arc inventory with wins
- Final producer inventory (13 kinds)
- Test suite growth (42 tests across 3 files)
- 7 sweep work_types on the 30-min timer
- Schema landings v65–v77
- Retrospective feedback memories captured during the arc
- Frontend surfaces overview
- What's not in scope for future work

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1908_ship3m.csv`). Same #200 WARN.
Ship 3'.m touched HTML/JS + one docstring + memory files —
zero RAG path change.

## Ship 3' arc — CLOSED

13 sub-arcs (a→m) delivered in a single day. Producer inventory
complete. Delivery validated. Retention landed. RLS + GRANT
parity swept. Inbox rendering + deep-links + per-row focus.
Data-quality closed on ISO 27001:2013→2022 renumbering.

## Related

- [[ship-3-prime-arc-retrospective-2026-07-17]] — full arc synthesis
- [[ship-3-prime-h-inbox-per-kind-rendering-2026-07-17]] — where the deferred UX polish originated
