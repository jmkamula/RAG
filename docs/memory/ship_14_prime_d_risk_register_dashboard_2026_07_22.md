---
name: ship-14-prime-d-risk-register-dashboard-2026-07-22
description: "Ship 14'.d — Risk register dashboard: sidebar nav + 4 tiles + 5x5 heatmap + top-5 + full list + drill-in detail panel"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.d (2026-07-22) — fourth sub-arc of Ship 14. Adds the
tenant-facing dashboard surface for the risks table + the 7
endpoints Ship 14'.c wired up. Consumers can now navigate to
Risk Register from the sidebar, see summary tiles + heatmap
+ top risks, drill in on any row.

## What ships

All changes in `static/arioncomply.html` — no backend touched.

### Sidebar nav

New "Risk register" entry between Cascade timeline and
Notifications, using `ti-alert-triangle` icon. Nav badge stub
`nb-risks` (hidden until Ship 14'.e wires it to
overdue/above-threshold counts).

`setMode('risks')` route registered.

### Toolbar

New toolbar with title + subtitle citing ISO 27005:2022 as
the grounding standard. Two buttons:
- **Template** — downloads the canonical xlsx from
  `/api/v1/tenant/risks/template` (Ship 14'.c static asset)
- **Refresh** — re-fetches summary + list

### Body layout

Loaded via `loadRisks()` which parallel-fetches
`/api/v1/tenant/risks/summary` + `/api/v1/tenant/risks?limit=500`.

Layout (top-to-bottom):

1. **4-tile row** — Total / Open / Overdue review / Residual ≥
   15/25. Each tile uses a coloured icon chip.
2. **Heatmap + Top-5 row** — 5×5 grid (Likelihood × Impact) with
   band colours (green ≤7, orange 8-14, red ≥15) beside a
   ranked top-5 list.
3. **Treatment-option + status breakdown** — inline pills for
   `Mitigate / Accept / Transfer / Avoid` counts + `open /
   in_progress / implemented / accepted` counts.
4. **Full list table** — all risks, sortable by score (server
   default). Columns: Ref / Threat+Asset / Score / Option /
   Status / Residual / Linked controls.

### Drill-in

`showRiskDetail(riskId)` fetches
`/api/v1/tenant/risks/{id}` and renders into the existing
detail panel:
- Header block: ext_ref + threat + asset
- 2-column stat block: Risk score (L×I) + Residual level
- Threat + vulnerability + owner
- **Treatment plan section** with all 5 schema_v87 columns
  labelled per 27005 §8.6.1 (rationale / resources / KPIs /
  constraints / cadence)
- Linked-controls section rendering the full list of
  program/extension/obligation refs — first-class

### Empty state

When `summary.total === 0`, shows a "No risks recorded yet"
empty state citing ISO 27005:2022 §8.6.1 and offering the
canonical template download.

## Ship 14'.a addendum — reviewer discipline answers

**1. Role split?**

Yes — `_linkedControlsInline()` and the drill-in linked-controls
section sort linked controls by role rank
(program → extension → obligation → guidance) and render them
side-by-side with a small role-band chip (colour-coded blue /
purple / red / grey per Phase 4b dashboard role band). No
primary/xfw split; all roles first-class in one visual list.

`_roleChipHtml()` is the display primitive; it never
hierarchically groups.

**2. Parallel CaseFile view?**

Not applicable — Ship 14'.d is UI-only. No CaseFile touched.
Ship 14'.e adds the case-file RISKS slot.

**3. Deterministic routing?**

Not applicable — no chat routing changes. UI-only.

**4. Guidance-normative discipline?**

Preserved — dashboard is a read-only view. Zero engine
mutations. Empty-state prose says "grounded in ISO 27005:2022"
without implying any new obligation.

## Verification

- Static HTML served through `/ui/arioncomply.html` returns
  all new elements: `nav-risks`, `body-risks`, `risks-wrap`,
  `loadRisks`, "Risk register" title.
- Balanced brace/paren counts across the 19,600-char new
  module region (130 `{` / 130 `}`, 144 `(` / 144 `)`).
- `_tile()` uniquely defined at line 1156 — no collision with
  existing helpers.
- Frontend consumes the 4 internal endpoints from Ship 14'.c:
  `/summary`, `/risks`, `/risks/{id}`, `/risks/template`.

Full browser walkthrough not scripted; smoke test relies on
the endpoint contract being unchanged since Ship 14'.c and
the DOM elements surfacing correctly.

## What did NOT ship

- **Nav badge counter** — placeholder stub for overdue +
  above-threshold count. Wired to actual data in Ship 14'.e
  alongside the notification producers.
- **Filters on the full list** — status / option filters
  client-side. Deferred; tenants can already filter server-side
  via query params.
- **Sortable columns** — table is server-ordered by risk_score
  DESC. Client-side sort deferred.
- **Bulk actions** (approve / archive selection) — deferred.
- **Add/edit modal** — canonical upload path stays primary;
  in-UI CRUD deferred to a future arc if partners request it.
- **DEMONSTRATES lineage in drill-in** — when a linked control
  is an obligation (e.g. `GDPR:2016/679:Art.32`), the drill-in
  currently shows the ref but doesn't traverse to the
  demonstrating program/extension sources. Deferred to
  14'.e alongside the chat-side DEMONSTRATES honouring.

## Ship 14 progress

| Sub-arc | Status |
|---|---|
| 14'.a Design + role-model + case-file addendum | ✓ |
| 14'.b schema_v87 + xlsx template + upload path | ✓ |
| 14'.c API surface (internal + external) | ✓ |
| **14'.d Dashboard cards + heatmap + drill-in** | **✓ (this doc)** |
| 14'.e Chat surfaces + cascade events | next |
| 14'.f Eval + retro | pending |

## Related

- [[ship-14-prime-c-risk-register-api-2026-07-22]] — the 7
  endpoints this UI consumes
- [[framework-role-model-arc]] Phase 4b — the role-band
  dashboard headers pattern this UI's role chips match
- Ship 14'.e: chat surfaces + cascade events — next sub-arc
- Ship 14'.f: eval cases + arc retrospective
