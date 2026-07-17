---
name: ship-3-prime-h-inbox-per-kind-rendering-2026-07-17
description: "Ship 3'.h — inbox per-kind icons, humanized labels for all 11 kinds, and one-click deep-link buttons to the target surface"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.h (2026-07-17) — makes the notification pipeline visible.

## Problem

Ships 3'.a-g wired 11 notification kinds end-to-end (schema →
producers → sweep → API → inbox row). The inbox rendered them
all through the same generic card:
- Bare `snake_case` label for kinds not in the 4-entry
  `_NOTIF_KIND_LABEL` map
- Same coloured dot for every kind
- No deep-link — tenant had to know which mode to jump to

The producers were building auditor signal that nobody could
act on without hunting through the app.

## What shipped

Two `static/arioncomply.html` additions:

1. **`_NOTIF_KIND_LABEL`** extended from 4 entries to 11:
   - `auto_resolved` → "auto-resolved"
   - `freshness_expiry` → "evidence stale"
   - `nc_surfaced` → "gap surfaced"
   - `upload_processed` → "upload processed"
   - `upload_failed` → "upload failed"
   - `stage2_proposal_ready` → "engine proposal ready"
   - `cite_verification_overdue` → "cited source needs re-verification"

2. **`_NOTIF_KIND_META`** — per-kind visual + navigation map:
   - Tabler icon class (ti-*)
   - Destination mode (`setMode()` target)
   - Action button label

3. **`renderInbox()`** refactor:
   - Icon replaces the coloured dot (colour still comes from
     `severity` palette)
   - New "Open X" button per row calls `_notifOpen(id, kind)`

4. **`_notifOpen(id, kind)`**:
   - Fire-and-forget PATCH to mark the notification read
   - `setMode(meta.mode)` to jump to the target surface

## Kind → destination table

| Kind | Destination mode | Rationale |
|---|---|---|
| threshold_crossed | cascade | cascade timeline shows the crossing |
| cascade_blocked | cascade | timeline explains the block |
| followup_overdue | cascade | followup lives on the timeline |
| implication_overdue | cascade | implication tracked on timeline |
| auto_resolved | cascade | FYI on cascade progress |
| freshness_expiry | dashboard | control drill-in shows evidence |
| nc_surfaced | dashboard | drill-in shows the new NC |
| upload_processed | docs | docs page shows the upload |
| upload_failed | docs | docs page shows the failure |
| stage2_proposal_ready | queue | Stage-2 tab holds the proposal |
| cite_verification_overdue | dashboard | drill-in shows the cited source |

## Scope decisions

Deep-links land the tenant in the target MODE, not on the
specific row. Adding per-row focus (scroll + highlight the
matching control_ref / upload_id / implication_id) would be
cross-cutting scope creep — each target loader would need to
consume a shared `window._notifTarget` global. Not shipped;
left as a follow-up if the "landing in the mode" UX proves
insufficient in tenant testing.

## No eval run

This arc is HTML/JS-only — no Python, no DB writes (beyond
smoke test cleanup), no RAG path touched. Running the full
208-case eval would burn LLM budget for zero signal because
the eval doesn't exercise the frontend. Skipping was defensible
here; baseline remains at 207/208 PASS + 1 WARN + 0 FAIL from
Ship 3'.g.

## Smoke tested

Seeded 3 notifications of different new kinds (stage2_proposal_
ready + upload_failed + cite_verification_overdue) via
`INSERT INTO tenant_notification`; confirmed the inbox
endpoint returns them with kind + severity + control_ref
intact; confirmed the served HTML at
`/ui/arioncomply.html` contains the new `_NOTIF_KIND_META` +
`_notifOpen` symbols. Cleaned up test rows.

## Related

- [[ship-3-prime-e-notification-producers-2026-07-17]]
- [[ship-3-prime-f-overdue-followups-2026-07-17]]
- [[ship-3-prime-g-cite-verification-overdue-2026-07-17]]
- [[dejargonize-ux-pass-2026-07-01]] — the humanized-label
  discipline this arc extends

## Producer inventory unchanged

Still 11 kinds. Remaining candidates:
- `posture_flip_to_comply` (UX only)
- `api_key_expiring` (needs schema addition on api_keys)
