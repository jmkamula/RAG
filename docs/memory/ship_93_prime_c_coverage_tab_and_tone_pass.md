---
name: ship-93-prime-c-coverage-tab-and-tone-pass
description: Ship 93'.c — closes the yellow-item arc with a browse-by-control aggregate rendered as a Dashboard "Coverage" tab. Bundled advisory-tone pass codifying that ArionComply speaks as advisor, not authority — Evidence Package export is the only auditor-tone surface.
metadata:
  type: project
---

# Ship 93'.c — Coverage aggregate + advisory-tone pass (2026-08-25)

## Framing

Ships 92-94 made yellow items (partial + missing MUSTs)
individually actionable inside the product:

- Ship 92'.b — MUST-overlap cite attestation prompts
- Ship 93'.a — `explain_partial()` close-path prose
- Ship 93'.b — upload affordance ("Upload evidence for X" button)
- Ship 93'.f — `explain_missing()` for MUSTs with zero coverage
- Ship 93'.z — housekeeping (retention sweep + arbiter partial
  explainability + closure trail schema)
- Ship 94'.a — LLM arbiter default ON
- Ship 94'.b — Evidence Package export reflects yellow-item picture

But the tenant still had to walk **control-by-control** to see
the total shape of what was incomplete. Every yellow item was
actionable individually; the aggregate wasn't visible.

Ship 93'.c closes the arc with a browse-by-control view of every
control with yellow items, prioritized by how close each is to
full coverage.

## The mid-arc pivot — "Fix workload" → "Coverage"

Initially built as a sidebar-first-class mode called "Fix
workload". Two design iterations pushed by operator feedback:

1. **Placement** — operator: "we have a notifications nav, i
   thought we could move a few of these there... i'm wondering
   the natural place for fix workloads, or should we change the
   name say partial, quick action or something or bundle it with
   notifications". Diagnosis: the surface is a browse-by-control
   cut of posture data — same substrate as the heatmap — so it
   belongs alongside Dashboard, not as a separate work-queue mode.
   Notifications is time-stamped events; Review queue is per-item
   approve/reject; Coverage is a browse view. Different idiom.

2. **Naming** — "Fix workload" carried two problems: "fix" is
   imperative (authority overtone flagged in this arc's tone
   audit), "workload" is corporate jargon. "Coverage" mirrors
   the tenant-facing language already in Evidence Package +
   partial_explainer ("3 of 7 required elements covered"), no
   imperative verb, sits naturally next to "Overview" as a
   Dashboard tab.

Landing: Coverage is a Dashboard tab (sibling to Overview
heatmap), not a sidebar entry.

## The advisory-tone pass

Operator flagged mid-arc: "we need to lay the truth as we know
it plainly, not auditor overtones or rubberstamp, just
completeness and best practice. user gets the sense that we are
advisory not authoritative."

Codified as [[feedback-advisory-tone-not-authoritative]]:

> Tenant-facing prose is advisor voice, not authority voice.
> ArionComply surfaces + tracks; the tenant + their auditor
> decide. Evidence Package export is the ONLY auditor-tone
> surface; every other surface speaks to the tenant.

Audit surfaced 9 offending phrases outside the Evidence Package:

- `api_server.py` — 4 sites: "auditor-grade explanation" in
  cite/cascade dismiss error strings + 2 docstrings labelling
  fields as "audit-grade"
- `static/arioncomply.html` — 4 sites: dismissal modal
  `prompt()` copy + "auditor-grade record, not a rubber-stamp"
  help text
- `rag/scheduler/tick.py` — 1 site: freshness notification
  body "auditor-ready"

All replaced with plain-language equivalents: "a specific
reason...that would make sense to someone reviewing this later"
/ "current" / etc. Ship 93'.c copy re-read under the new rule
came out clean by construction — neutral state labels ("Ready
to close", "In progress", "Not started") + advisory descriptions
("Adding one column or uploading one document typically moves
each to full coverage").

## Delivered

1. **New endpoint** `GET /api/v1/dashboard/coverage`
   - 3-bucket aggregate: `ready_to_close` (≥1 partial MUST) /
     `in_progress` (some direct evidence + ≥1 missing) /
     `not_started` (no direct evidence)
   - Within each bucket sorted `(n_partial DESC, n_direct DESC,
     control_ref ASC)`
   - Top-K per bucket enriched with per-control top-N yellow
     items + close-path prose
   - **Bridge-covered MUSTs excluded** from n_missing (they're
     covered by xfw evidence — not yellow items)

2. **New module** `rag/posture/coverage.py` (~380 LOC)
   - `build_coverage()` reads `posture_must_verdicts` SSoT
   - LEFT JOINs `posture_must_bridge_coverage` for bridge
     exclusion at SQL layer
   - `_close_path_prose()` branches:
     * workbook partial → `explain_partial()`
     * doc-extractor partial (no workbook mapping) →
       `explain_missing()` with "Partial evidence on file for X
       — to move to full coverage" reframe (prepends acknowledgment
       so the missing-branch prose doesn't read as contradictory)
     * missing → `explain_missing()` verbatim

3. **Dashboard "Coverage" tab**
   - Toolbar gets `Overview` + `Coverage` tabs (parallel to
     Review Queue Stage-1/2 tab pattern)
   - `body-dashboard` splits into `dash-tab-overview` +
     `dash-tab-coverage`
   - `setDashTab()` switches; `refreshDashTab()` dispatches
     Refresh button per active tab
   - `#dashboard?tab=coverage` hash-route wired for deep-links
   - `setMode('dashboard')` resets to Overview for predictable
     behavior

4. **Coverage renderer**
   - Header + 3 bucket cards
   - Each control card: `standard_display` + control_ref +
     business title + counts (partial + missing + direct-on-file)
     + top-3 yellow items with close-path prose inline
   - Bucket accent color + Tabler icon per bucket
   - Deep-links to `#dashboard?control=X` drill-in via
     `_openControlDetail`

## Dogfood (ISO Arion)

- **14 controls ready to close** (18 partial MUSTs)
- **64 controls in progress** (some evidence + gaps)
- **37 controls not started** (no evidence yet)
- **1693 missing MUSTs total** (down from raw 3218 pre-bridge-
  exclusion — bridge coverage removes 1525 from the yellow
  picture)
- Endpoint latency: 1.0s for 60 enriched controls + 156 yellow
  items with per-item close-path prose (module-cache-warmed)

## What doesn't change

- No new schemas
- No changes to chat pipeline / classifier / consensus
- Review Queue, Notifications, Cascade untouched
- Dashboard Overview (heatmap + framework summary) untouched

## Eval

232 PASS + 1 WARN + 0 FAIL (baseline preserved).

## Codified lessons

**Lesson 118: Placement follows semantics.** "Fix workload"
initially got a sidebar-first-class entry because it looked like
"a mode the tenant lives in." But semantically it's a
**browse-by-control cut of posture data** — same substrate as
the heatmap. That's Dashboard-tab shape, not sidebar-mode
shape. Rule: before allocating sidebar real estate, ask "what
data is this a view of, and where does that data already live?"
Different-view-of-same-data goes as a tab under the existing
mode; genuinely-new-work-idiom earns a sidebar entry.

**Lesson 119: Advisory-tone audit needs a rule + a pass, not
just habit.** The tone had drifted "audit-grade" into 9 places
across `api_server.py`, the SPA, and one notification body —
none of them auditor-facing surfaces. Habit + review caught most
of it; the codified rule
([[feedback-advisory-tone-not-authoritative]]) makes future drift
detectable + testable. Rule: authoritative language on
tenant-facing surfaces requires an explicit justification;
absence of justification means fix.

**Lesson 120: Naming carries tone.** "Fix workload" → "Coverage"
wasn't a UX renaming — it was a tone renaming. "Fix" is
imperative (authority overtone). "Workload" is corporate jargon.
"Coverage" is the exact word the tenant-facing prose already
uses in Evidence Package + explain_partial ("3 of 7 required
elements covered"). Lesson: when in doubt about surface naming,
grep the existing tenant-facing prose for the concept — the word
that's already earned tenant-facing use is usually the right one.

## Related

- [[ship-93-prime-a-partial-explainability]] — where
  `explain_partial()` was built
- [[ship-93-prime-f-missing-musts]] — where `explain_missing()`
  was built
- [[ship-93-prime-z-housekeeping]] — closure trail schema
- [[ship-94-prime-a-arbiter-cutover]] — LLM arbiter default ON
  pre-Coverage
- [[ship-94-prime-b-evidence-package-yellow-items]] — auditor-
  facing export reflecting the yellow-item picture
- [[feedback-advisory-tone-not-authoritative]] — the tone rule
  codified in this arc
- [[dejargonize-ux-pass-2026-07-01]] — sibling to this pass;
  covered tenant-facing prose conventions
- [[product-principle-cite-expose-and-track]] — same
  positioning applied to cite semantics
