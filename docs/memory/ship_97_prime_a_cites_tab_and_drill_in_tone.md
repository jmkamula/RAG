---
name: ship-97-prime-a-cites-tab-and-drill-in-tone
description: Ship 97'.a — moved the Cite reviews due + attestation match confirmation panels off the Dashboard into a new Review Queue "Cites" tab. Dashboard becomes summary-only (KPI tile + heatmap, no per-row action panels). Bundled tone fix — drill-in and topic-detail card reworded from auditor-prep frame to "defend your posture 24×7" frame per operator's tone push.
metadata:
  type: project
---

# Ship 97'.a — Cites tab + drill-in tone (2026-08-26)

## Framing

Operator on the Dashboard:

> "i want to find the right home for these" — pointing at the
> `Cite reviews due (periodic)` and `New evidence — confirm match`
> panels stacked below the KPI tiles

Semantic split we agreed on:

- **Dashboard** = ambient overview. Looking, not doing. Heatmap +
  KPI tiles + framework summary.
- **Review Queue** = queue-shaped work with per-row action buttons.
  Doing.
- **Notifications** = time-stamped events + retro info.

The two cite panels had per-row `Verify` / `Confirm` / `Not the
same` buttons — queue-shaped work. Dashboard was hosting both
looking-and-doing. Move to Review Queue as a new "Cites" tab
(third alongside Intake approval + Posture approval).

While reviewing the drill-in for one of these controls (Art.30
RoPA), operator also flagged:

> "i can still see the Auditor tone. we are not preparing our
> users for audit, we want them to be compliant 24×7 and defend
> their posture at time of impact, for which audit could be one
> on them."

That's a product-principle push. The audit is a moment; the
compliance program is 24×7 defense. Tenant-facing prose should
frame around "posture you defend" rather than "artifacts your
auditor will accept."

Bundled the tone rewrite into Ship 97'.a — same UX arc, same
file touched, tight scope.

## Delivered

### 1. Cites tab in Review Queue

**One file changed** — `static/arioncomply.html`. No backend
touched.

- New `stab-cites` tab in the Review Queue toolbar. `setStage()`
  now accepts either integer `1`/`2` or the string `'cites'`.
- `loadCitesQueue()` fetches both cite endpoints in parallel +
  reuses the existing `renderCiteFreshnessCard` +
  `renderCiteAttestationsCard` renderers unchanged. Portable
  panels — return HTML strings, no dashboard-specific DOM ids.
- Empty state on the tab: "No cite reviews or match confirmations
  waiting."
- `loadStageCounts()` extended to compute the Cites tab pill
  count + include it in the nav badge sum.
- Hash routing extended — `#queue?tab=cites` supported.

### 2. Dashboard cleanup

Two panels removed from `renderDashboard`:

- `renderCiteFreshnessCard` — no longer lands on Dashboard.
- `renderCiteAttestationsCard` — same.

Dashboard is now summary-only for cites: the KPI tile shows the
count + a click routes to the tab.

### 3. KPI tile broadened

`Cite reviews due` (freshness only) → `Cites` (freshness +
attestations). Rationale: both types land on the same Cites tab
so the tile should count both. Sub-line lists whichever
categories are non-zero:

    Cites  7
    4 stale · 3 to confirm

Click behavior changed from `scroll-to-panel` to
`setMode('queue'); setStage('cites')`.

### 4. Notification deep-link routing

`_NOTIF_KIND_META[cite_verification_overdue]` route:
`dashboard → 'Open control'` → `queue → 'Open Cites tab'` with a
new `extra.stage` field. `_notifOpen()` reads
`meta.extra.stage` when the destination is `queue` + calls
`setStage()` after `setMode()`. Small extension of the meta
schema; other kinds unaffected.

### 5. Drill-in tone rewrite

Same file, same commit.

**`renderBridgeChip` — asserted-mapping chip on missing MUSTs:**

Was:
> Related **A.5.9, 7.5** controls are asserted (per ArionComply
> catalog) to implement one or more of these missing elements.
> **Auditor-defensibility depends on the specific evidence and
> mapping acceptance.**

Now:
> **A.5.9, 7.5** controls in another framework are mapped (per
> ArionComply catalog) to contribute coverage for one or more of
> these elements. **How strongly they defend this posture depends
> on the specific evidence you have in place there.**

Same warning ("bridge coverage isn't a guaranteed shield") but
tenant-frame ("your posture", "your evidence") instead of
auditor-frame ("auditor-defensibility").

**Demonstrated-by header (`renderDemonstratedBy`):**

Was:
> **Demonstrated by** — propagates to [OFI]
> (auto-inferred: no direct assessment)
> Cross-framework grounding — implemented by the operational
> controls below.

Now:
> **Coverage from your other frameworks** — posture here reflects
> [OFI]
> (inferred from below — no direct assessment)
> Coverage from other frameworks — evidence you already have on
> the operational controls below contributes here.

Same information, tenant-perspective.

**Topic-detail card header:**

Was: `What auditors expect`
Now: `What good coverage looks like`

**Confirm-reason textarea placeholder** (2 sites):

Was: `Note for audit trail...`
Now: `Note for the record...`

Header comment on `renderBridgeChip` updated too — "The auditor
decides whether the assertion + the tenant's evidence hold" →
"whether the coverage holds up in practice depends on the
tenant's specific evidence there".

### 6. Regression guards (Ship 96'.c pattern)

3 new tests in `test_notification_producers.py`
(37 → 40 tests, all pass):

- `test_no_auditor_defensibility_string_in_spa` — locks the
  drill-in bridge chip rewrite
- `test_no_what_auditors_expect_header_in_spa` — locks the
  topic-detail card header rewrite
- `test_no_note_for_audit_trail_placeholder_in_spa` — locks the
  textarea placeholder rewrite

Same pattern as Ship 96'.c Lesson 133: target the specific fixed
strings, don't attempt general tone linting.

## Dogfood (ISO Arion)

Before Ship 97'.a:

- Dashboard header stacked: heatmap + KPI tiles + Cite reviews
  panel (4 stale) + Cite attestations panel (3 pending)
  + Implications panel + Followups panel
- Drill-in bridge chip: "Auditor-defensibility depends on..."

After Ship 97'.a:

- Dashboard header: heatmap + 3 KPI tiles (Follow-ups 0 /
  Coverage 115 / Cites 7). Only cascade-action panels remain
  below (unchanged this arc).
- KPI Cites tile shows `7` with sub `4 stale · 3 to confirm`.
- Click Cites tile → Review Queue > Cites tab shows the same
  two panels the Dashboard used to render.
- Drill-in bridge chip: "How strongly they defend this posture
  depends on..."

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved (SPA only, no
LLM pipeline touch).

Producer + parity + tone-guard tests: 40/40 pass.

## Codified lessons

**Lesson 135: Semantic split principle — looking vs doing vs
alerting.** Dashboard, Review Queue, Notifications each have a
clear job. When a surface starts hosting a mix (Dashboard with
per-row action panels), the tenant loses the mental model of
"where do I go for X?" Rule: when adding a new panel, ask if
it's looking, doing, or alerting — put it in the mode that
matches. When retiring or moving a panel, keep the split clean
by placing it in ONE home and only summarizing elsewhere.

**Lesson 136: Product tone reveals product principle.** The
"Auditor-defensibility depends on..." phrasing on the drill-in
was technically accurate but framed the tenant as an audit-prep
subject. Rewriting to "How strongly they defend this posture"
reframes the tenant as an ongoing defender of their program —
which IS the product principle. Tone isn't cosmetic; it's the
product's stated value showing up in text. Rule: when a tone
edit lands, ask what product-principle claim it makes. If the
principle isn't right, don't just soften the words — align them
with what the product actually helps the tenant do.

**Lesson 137: Bundle tone fixes with the UX arc that surfaced
them.** Ship 96'.c's tone fixes were a standalone arc after the
audit found the offenders. Ship 97'.a's tone offenders were
surfaced by operator walking through the destination the tile
click created. Rewriting in the same commit that moved the
panels is tighter — the tenant's flow (Dashboard → click →
land on drill-in) was tested end-to-end as one experience.
Rule: when the arc is a UX experience audit, keep tone within
scope; when the arc is source discipline (parity guards,
producer wiring), tone is separate. Different discipline for
different arc-shape.

## Related

- [[ship-95-prime-a-dashboard-kpi-restructure]] — the KPI tile
  restructure that this arc completes (Dashboard now truly
  summary-only for cites)
- [[ship-96-prime-a-notification-kind-audit]] — the deep-link
  meta schema this arc extended with `extra.stage`
- [[ship-96-prime-b-cascade-timeline-ux]] — sibling
  "add-actionable-section-to-a-different-home" pattern
- [[ship-96-prime-c-notification-tone-rewrite]] — the tone-guard
  pattern this arc reused (regression guards target specific
  fixed strings)
- [[feedback-advisory-tone-not-authoritative]] — the tone rule
  applied
- [[dejargonize-ux-pass-2026-07-01]] — the sibling conventions
