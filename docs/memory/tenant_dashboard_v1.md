---
name: tenant-dashboard-v1
description: "SHIPPED 2026-05-26: tenant-scoped Dashboard view (heatmap + per-framework summary + interactive drill-to-chat) as the new default landing surface."
metadata: 
  node_type: memory
  type: project
  originSessionId: 23cb7b33-d854-4985-9f9a-c02de86209a1
---

**Status: SHIPPED 2026-05-26.**

User-requested feature: a tenant dashboard as an extension of the chat app, with (1) summary heatmap, (2) frameworks & tenant posture, (3) interactive drill from NC/OFI to remediation chat. Decisions captured via AskUserQuestion before coding:
- **Placement:** Replace Chat as the default landing view. Dashboard is the first nav item; Chat moves to the second.
- **Heatmap grouping:** ISO 27001 by Annex A theme — Organisational (A.5), People (A.6), Physical (A.7), Technological (A.8), Management (4–10). GDPR by two chapter groups: Principles & lawfulness (Art.1–11), Controller, transfers & rights (Art.12+).
- **Drill flow:** Click cell → detail panel → "Ask the assistant" switches to chat tab and **prefills** the input ("how do I remediate <ref>?" for NC/OFI; "tell me more about our posture on <ref>" otherwise). User reviews and hits send.

**Backend** (`api_server.py`): new `GET /api/v1/dashboard/posture` returns `{frameworks: [{standard_id, display_name, summary, groups: [{label, controls: [{control_ref, finding, confirmation_status, gap_excerpt, engine_proposal_status, engine_proposed_finding}]}]}]}`. Tenant-agnostic — works for any tenant whose `posture_controls` rows are loaded. Path registered BEFORE `/api/v1/posture/{control_ref}` so FastAPI doesn't route "dashboard" as a control_ref.

**Frontend** (`static/arioncomply.html`):
- New `Dashboard` nav item + `body-dashboard` panel.
- Heatmap = CSS grid of 13×13px coloured cells, one per control. Hover tooltip carries `<ref> — <finding>`. Click opens the detail panel.
- Per-framework card: total in scope, stacked horizontal bar with %ages by finding, headline counters.
- Detail panel for dashboard cells **replaces** the queue's confirm/override tabs with a single "Ask the assistant" button (configureDashboardActions). configureActionPanel re-injects the queue UI when the user switches back to a queue card — the dashboard handler does an innerHTML replace, so the queue rebuild has to be defensive.
- `closeDetail` now also clears `.heat-cell.active`, parallel to the existing `.qcard.active` cleanup.

**Default landing:** `let mode = 'dashboard'` and `connect()` now dispatches to `loadDashboard()` when mode is 'dashboard'. This is the only behavioural change to the existing chat/queue/docs flows.

**Display names normalized** (so the UI doesn't show machine ids): `ISO27001:2022` → "ISO 27001:2022", `GDPR:2016/679` → "GDPR (EU 2016/679)", `ISO27701:2019` → "ISO 27701:2019". Fallback is the raw standard_id.

**Observed on Arion tenant**:
- ISO 27001: 106 controls in scope, distributed across 5 themes. A.7 (Physical) is mostly N/A — consistent with a SaaS tenant.
- GDPR: 303 articles, 288 "Not assessed" — that's the long tail of unreviewed GDPR articles. The grey cells communicate "scope is big, review coverage is partial." User intent is to drive that down over time.

**Body clause oddity to investigate (follow-up):** ISO 27001 "Management (4–10)" group renders refs like `X.B3CF.99` rather than `5.1` / `9.3`. The Annex A theme parser works correctly (controls with `A.5.` etc. routed properly); these X-prefixed refs are placeholder body-clause IDs in the posture_controls rows. Not a dashboard bug — likely an intake/seed issue. Capture: low priority, doesn't break the heatmap.

**Not yet covered by eval:** the dashboard endpoint and UI are not exercised by tests/eval_suite.py (which is chat-only). A backend regression test for `/api/v1/dashboard/posture` would be straightforward — assert tenant scope is honored, finding distribution sums to total, group ordering is canonical. Worth adding next.

Related: [[hitl-two-stage-approval-design]], [[stage1-detail-show-inference-chain-idea]], [[engine-nc-at-zero-satisfied]], [[posture-discipline-dup-label-fix]].
