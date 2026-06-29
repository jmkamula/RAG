---
name: dashboard-cite-freshness-card-2026-06-27
description: "SHIPPED 2026-06-27 (5719fbf): dashboard freshness card — `GET /api/v1/dashboard/cites/needs-verification` buckets cites red/yellow/upcoming via SQL CASE on (last_verified_at + cadence + grace) vs now() and next_review_due window. UI renders banner card on dashboard with per-row Verify buttons that refresh dashboard state on modal close via MutationObserver. Closes one of the four deferred items from cite-mode v1 frontend. Eval 198/199 effective."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

### Backend (`api_server.py`)

`GET /api/v1/dashboard/cites/needs-verification?upcoming_window_days=7`
— single SQL CTE with CASE buckets each active cite into:

- **red** — `last_verified_at IS NULL` OR `now() > last_verified_at +
  (cadence_days + grace_days)` where `grace_days = LEAST(GREATEST(
  cadence_days / 10, 1), 30)`
- **yellow** — past `next_review_due` but still in grace window
- **upcoming** — `next_review_due <= now() + window_days`
- **fresh** — excluded from response

GROUP BY `(leaf_id, system_id, system_name, bucket)` then ORDER BY
priority (red → yellow → upcoming) + bucket-internal ordering by
days_overdue / days_until_due. Returns `{counts: {red, yellow,
upcoming}, buckets: {red: [...], yellow: [...], upcoming: [...]}}`.

Each row includes: control_ref (parsed from leaf_id), leaf_label
(humanised leaf_id), system_name (joined), must_count (cites in the
group), last_verified_at, next_review_due, days_overdue (red/yellow)
OR days_until_due (upcoming).

### Frontend (`static/arioncomply.html`)

- `loadDashboard()` now Promise.all-fetches `posture` + `freshness`
  with `.catch(() => null)` fallback (forward compat — if the
  endpoint is absent, dashboard still loads).
- `renderDashboard(d, freshness)` prepends optional `freshnessHtml`
  only when at least one bucket non-empty.
- `renderCiteFreshnessCard(freshness)` — banner-style card:
  headline "{red} stale · {yellow} due now · {upcoming} due soon" +
  toggle button + three sections (one per bucket) with row layout:
  `<control_ref> <leaf_label> ↗ <system> · N MUSTs · <overdue/due-in>`
  + per-row "Verify" button.
- `openCiteVerifyFromCard(controlRef, leafId, systemId, systemName)`
  — wraps existing `openCiteVerify`, attaches `MutationObserver` to
  detect modal close, then triggers `loadDashboard()` so the card
  reflects the post-verify state without manual refresh.

## SQL %% escape gotcha (caught + fixed mid-smoke)

Initial query had `× 10%` in a SQL comment. psycopg2's `%s`
substitution treats bare `%` as a format token; the query failed
with `IndexError: tuple index out of range`. Fix: replaced `10%`
with `10pct` in the comment text. **Future rule**: when writing SQL
strings for psycopg2, NEVER use bare `%` even in comments. Use
`%%` to escape or write `pct` / `percent` instead.

## Smoke verified

All four states confirmed by manipulating a test cite's
`last_verified_at` + `next_review_due` via direct DB UPDATE:

1. Fresh (verified now, 60d to next_review_due) → counts all zero
2. Upcoming (5d to next_review_due, default 7d window) → upcoming=1
3. Yellow (2d past next_review_due, in 9d grace) → yellow=1
4. Red (10d past grace) → red=1

Eval 198/199 effective post-ship — 196/199 raw + #16 + #21 re-runs
pass (variance). #27 is documented state-drift (Stage-1 queue
empty after the 2026-06-27 sweep, not caused by this work).

## Why the new render path

The existing dashboard already had a posture heatmap + per-framework
summary. The freshness card sits ABOVE both as a banner — it's the
"act on this now" surface, distinct from the posture overview. UI
toggle hides it once tenant decides "not today" without losing the
underlying counts.

## What's still deferred (v2)

From the cite-mode v1 frontend memo's four-item deferred list, one
done (this card); three remain:

- Catalog validation on cite PUT (must_id format-only today)
- Verification log viewer in UI
- Journey wizard onboarding question to seed `tenant_external_system`
  rows at first sign-in
- JS `isCiteAcceptable()` predicate mirror for resilience

## Related

- [[cite-mode-v1-backend-2026-06-27]] — endpoint family this extends
- [[cite-mode-v1-frontend-2026-06-27]] — UI lane this complements
  (cited lane on the leaf panel = the source of truth; this card =
  the dashboard aggregation)
- [[product-principle-evidence-stored-vs-cited]] — the design that
  motivates surfacing freshness prominently
- [[product-concept-evidence-cascade-2026-06-27]] — strategic
  successor that builds on this card's data surface
