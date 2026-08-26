---
name: ship-95-prime-a-dashboard-kpi-restructure
description: Ship 95'.a — Dashboard KPI header restructured from 5 cascade-heavy retro tiles to 3 tenant-actionable ones. Follow-ups (merged from two overlapping tiles) / Coverage (new, links to Ship 93'.c tab) / Cite reviews due. Tiles clickable, retro data preserved on existing surfaces.
metadata:
  type: project
---

# Ship 95'.a — Dashboard KPI restructure (2026-08-25)

## Framing

The Dashboard KPI header was designed during Ship 3' when Cascade
was the featured surface. It carried 5 tiles:

    Follow-ups | Expected next steps | Muted cascades (30d)
    Auto-closed (7d) | Verifications (7d)

Two problems by 2026-08:

1. **Cascade-metric skew**. All 5 tiles feed off cascade tables.
   On healthy tenants the numbers stay at zero or near-zero — the
   header dedicates ~1/6 of the dashboard viewport to metrics that
   rarely move.

2. **Semantic overlap that confuses at glance-value**. "Follow-ups"
   (`triggered_implication.pending`) and "Expected next steps"
   (`expected_followup_event.pending`) come from different cascade
   tables but read as the same thing at KPI granularity. The
   internal distinction (obligation-oriented vs event-oriented) is
   engine mechanics; the tenant sees two "what do I need to do?"
   tiles.

3. **Retro tiles displaced actionable ones**. Muted / Auto-closed
   / Verifications are all rear-view metrics. Meanwhile the Ship 93'.c
   Coverage aggregate (14 controls ready to close, 101 more with
   gaps on ISO Arion) didn't get header representation — the tenant
   had to click Dashboard's new Coverage tab to see the biggest
   actionable surface.

Operator surfaced this in a UX walkthrough of the dashboard header,
asking how the tenant would use each tile. Answer: they mostly
wouldn't.

## Delivered

**Header shrunk from 5 tiles to 3, each clickable + hover-highlighted:**

| Tile | Value | Deep-link |
|---|---|---|
| Follow-ups | `triggered_implications.pending + expected_followups.pending` (merged) | `setMode('cascade')` |
| Coverage | Sum of Coverage bucket totals | `setDashTab('coverage')` |
| Cite reviews due | Freshness `red + yellow + upcoming` | scrolls to the Cite freshness panel below |

Sub-line surfaces the actionable dimension (`N overdue · on M
controls`, `N ready to close · M more with gaps`, `N stale · M
due soon`). Accent color (red / amber / green / none) matches
urgency. Any-activity gate now checks all three tiles — the strip
stays invisible when everything is clean.

**Retired tiles + where the retro data still lives:**

| Retired | Reachable via |
|---|---|
| Muted cascades (30d) | Cascade timeline (`kind=suppression`) + Profile → Cascade overrides section |
| Verifications (7d) | Cascade timeline (`kind=verification`, filter `since_days=7`) |
| Auto-closed (7d) | Ship 95'.b (Notifications inbox — kind='auto_resolved' producer wire) |
| Expected next steps | Merged into Follow-ups tile |

**Fast-path endpoint** `summary_only=1` added to
`/api/v1/dashboard/coverage`. Skips per-control enrichment (no
close-path prose, no Neo4j titles) — returns only bucket counts.
**87ms vs 1.0s.** Used by the Dashboard KPI tile; the Coverage tab
still uses the full path.

## Dogfood (ISO Arion)

    Follow-ups: 0        (nothing waiting)
    Coverage:   115      (14 ready to close · 101 more with gaps)
    Cite reviews due: 4  (4 stale)

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved.

## Codified lessons

**Lesson 121: KPI strips age when their underlying arcs mature.**
The Ship 3'-era cascade-heavy KPI strip made sense when Cascade was
the featured surface. Two years of arcs later, Coverage + Cite
attestation are the actionable daily-drivers; the cascade metrics
stayed at zero on most tenants. Rule: when you add a new tenant-
facing surface (Ship 93'.c Coverage tab, Ship 92'.b cite
attestation), audit the Dashboard header for tile-worthiness. The
header is finite real estate — new arcs earn tiles by displacing
older ones, not by squeezing in.

**Lesson 122: Retirement without a reachability audit is data
loss.** Dropping the Muted / Verifications / Auto-closed tiles
looked like a simple visual change. In fact only 2 of the 3 retros
had homes on other surfaces — Auto-closed had no producer and no
alternative surface at all. Fixed by Ship 95'.b (producer wire). Rule:
before retiring any tenant-facing metric, prove it's still reachable
elsewhere. If it isn't, either restore the surface or ship the
producer/log surface first.

**Lesson 123: Fast-path query params preserve heavy endpoint
utility.** The Coverage endpoint takes ~1s to build the full
enriched payload (top-K per bucket with close-path prose). Fine for
the Coverage tab; too slow for a KPI tile in a `Promise.all` of 8
dashboard fetches. `summary_only=1` skips the enrichment step and
returns in 87ms — same endpoint, two consumers with different
latency needs. Rule: when a lightweight consumer wants a subset of
a heavy endpoint's payload, add a query param that skips the
expensive work rather than either (a) blocking the light consumer
on the heavy work, or (b) building a parallel summary endpoint.

## Related

- [[ship-93-prime-c-coverage-tab-and-tone-pass]] — the Coverage tab
  the new KPI tile deep-links to
- [[ship-92-prime-b-cite-attestation]] — the Cite reviews panel the
  third KPI tile scrolls to
- [[ship-95-prime-b-auto-resolved-producer]] — the retro-
  reachability follow-up (closes the Auto-closed data gap)
- [[feedback-advisory-tone-not-authoritative]] — the tone rule
  applied through the KPI copy
