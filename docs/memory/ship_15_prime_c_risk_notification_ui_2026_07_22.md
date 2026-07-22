---
name: ship-15-prime-c-risk-notification-ui-2026-07-22
description: "Ship 15'.c — notification inbox drill-in for 4 risk kinds: humanized labels + Tabler icons + one-click deep-link to risks mode + auto-open detail panel"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 15'.c (2026-07-22) — third sub-arc of Ship 15. Ships the
notification-inbox UI treatment for the 4 risk kinds
(`risk_added`, `risk_treatment_overdue`,
`residual_above_threshold`, `risk_review_due`) that Ship 14'.f
enabled at the database level. Follows the Ship 3'.h/i pattern.

## What ships

All changes in `static/arioncomply.html` — no backend touched.

### Humanized labels (`_NOTIF_KIND_LABEL`)

Added 4 entries so `humanizeNotifKind(k)` produces friendly
prose in the inbox rows:

- `risk_added` → "new risk added"
- `risk_treatment_overdue` → "risk treatment overdue"
- `residual_above_threshold` → "residual risk above threshold"
- `risk_review_due` → "risk review due"

### Icon + action metadata (`_NOTIF_KIND_META`)

Added 4 entries routing all 4 kinds to `mode: 'risks'` with
`actionLabel: 'Open risk'`. Distinct Tabler icons per kind:

- `risk_added` → `ti-plus-square`
- `risk_treatment_overdue` → `ti-clock-exclamation`
- `residual_above_threshold` → `ti-alert-triangle`
- `risk_review_due` → `ti-calendar-event`

### Deep-link target attributes on risk table rows

Both the top-5 rows and the full-list rows in the Risks
dashboard now carry `data-focus-entity="{risk_id}"` — matching
the notification's `related_entity_id`. When `_applyNotifFocus()`
fires after mode switch, it scrolls the matched `<tr>` into
view + adds the `notif-focus-flash` class for a 2.2s highlight.

### Auto-open drill-in for risk deep-links

`renderRisks()` now calls `_applyNotifFocus()` at the end, and
if the pending target is a risk kind, calls
`showRiskDetail(entity_id)` after a 120ms delay. Effect: click
"Open risk" on any risk notification → the risks mode opens →
the matching row highlights → the drill-in panel auto-opens
with full treatment plan visible.

## Verification (end-to-end contract)

Inserted a synthetic `risk_added` notification via direct SQL
with `related_entity_id = R001.id`. Fetched
`/api/v1/tenant/notifications?limit=3` → the row surfaces with:

```
kind=risk_added
entity_id=c0a504d0-00ca-4698-afd3-46869c2271fb
title=New risk R001 added to the register
```

Client-side render chain (verified via HTML fetch):
- Row header: "new risk added" chip visible
- Icon: `ti-plus-square` glyph
- Button: "Open risk"
- On click: `_notifOpen('...', 'risk_added', null, 'c0a504d0-...')`
  → sets `window._notifTarget = {kind, ref: null, entity_id}`
  → `setMode('risks')` triggers `loadRisks()`
  → after render: `_applyNotifFocus()` scrolls + flashes the
    matching `<tr>` → `showRiskDetail(entity_id)` auto-opens
    the drill-in panel

Cleanup performed after test.

## Ship 14'.a addendum alignment

**1. Role split?**

Preserved — the drill-in panel that auto-opens is Ship 14'.d's
`_renderRiskDetail`, which renders linked controls with role
band chips sorted by program → extension → obligation →
guidance rank.

**2. Parallel CaseFile view?**

Not applicable — UI-only sub-arc, no chat surfaces touched.

**3. Deterministic routing?**

Not applicable — no LLM inference. Client-side event handlers
route deterministically based on the `mode` field in
`_NOTIF_KIND_META`.

**4. Guidance-normative discipline?**

Preserved — cosmetic labels + icons only. No engine mutations.

## What did NOT ship

- **Filter-by-kind UI** — the inbox filter still supports only
  read/unread/dismissed; a "show only risks" filter isn't
  wired. Existing kind-based filtering via the API's `kind[]`
  filter (Ship 4'.d external endpoint) could feed a
  dropdown, but the inbox is already fairly compact.
- **Bulk-action UI** — "mark all risk_treatment_overdue as
  read" style. Existing per-row buttons are enough for now.
- **Live toast on new-risk-added event** — no websocket / SSE
  channel exists in the app; tenants see risk_added on next
  page refresh or the 30-min notification-delivery sweep.

## Ship 15 progress

| Sub-arc | Status |
|---|---|
| 15'.a POST + PATCH + DELETE + emit_risk_added | ✓ |
| 15'.b Workbook importer INSERT detection + producer | ✓ |
| **15'.c Notification UI drill-in for 4 risk kinds** | **✓ (this doc)** |
| 15'.d DEMONSTRATES traversal + SDK typed methods | next |
| 15'.e Eval cases + arc retrospective | pending |

## Related

- [[ship-14-prime-f-risk-notifications-2026-07-22]] — the
  producer that populates the notifications this UI renders
- [[ship-14-prime-d-risk-register-dashboard-2026-07-22]] —
  the drill-in panel this arc auto-opens
- Ship 3'.h/'.i (implicit via CLAUDE.md) — the humanizer +
  Tabler icon + one-click deep-link pattern this arc mirrors
