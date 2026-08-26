---
name: ship-96-prime-b-cascade-timeline-ux
description: Ship 96'.b — Cascade timeline UX pass. The Ship 95'.a Follow-ups tile deep-linked here promising "here's what needs doing" but the destination showed a mixed chronological stream with no action affordance. Fixed by prepending an "Follow-ups due" section (reusing the Dashboard's action panels) + rewording the toolbar + sidebar labels to advisory tone.
metadata:
  type: project
---

# Ship 96'.b — Cascade timeline UX check (2026-08-26)

## Framing

Ship 95'.a's Follow-ups KPI tile deep-linked to Cascade timeline
(`setMode('cascade')`). Tile promise: "here's what needs doing"
— `X pending · Y overdue on Z controls`. Actual destination:

- Chronological stream mixing verifications + implications +
  followups + suppressions
- No status filter — pending items buried among last-30-day history
- No action buttons on rows — tenant couldn't satisfy or dismiss
  from the timeline; had to click through elsewhere
- **The Dashboard actually had BETTER action affordance** than the
  deep-link destination — `renderTriggeredImplicationsPanel` there
  shows pending items with satisfy/dismiss buttons

So the KPI tile click was a UX regression from the pre-95'.a
world: tenant went from "click Dashboard, see pending items with
buttons" to "click KPI tile, land on a wall of history where the
buttons don't exist."

## Delivered

**One file changed** — `static/arioncomply.html`. No backend
touched.

1. **"Follow-ups due" section prepended to the Cascade timeline**
   using the SAME renderers the Dashboard uses
   (`renderTriggeredImplicationsPanel` +
   `renderExpectedFollowupsPanel`). Same satisfy/dismiss/bulk
   buttons; same visual language. Section is entirely hidden when
   both panels have nothing to render.

2. **`loadCascadeTimeline` now fetches 4 URLs in parallel**
   (timeline + pending implications + pending followups + overdue
   followups) instead of 1. Same pattern the dashboard loader uses.

3. **Toolbar reworded to reflect the two-section structure:**
   - Title: `Cascade timeline` → `Follow-ups & activity`
   - Subtitle: `Chronological log of every cascade emission —
      verifications, implications, followups, suppressions` →
     `Actions due today plus a chronological view of recent
      cascade activity`
   - Recent-activity chip labels dropped snake-case:
     `implications` → `follow-ups`, `followups` → `next steps`,
     `suppressions` → `muted`

4. **Sidebar nav label reworded** — `Cascade timeline` →
   `Follow-ups`, with hover title explaining the full scope
   (advisory-tone rule: label is what tenant reads at a glance,
   title carries the technical detail).

## Design notes

**Why reuse the existing renderers** — the two panels
(`renderTriggeredImplicationsPanel` +
`renderExpectedFollowupsPanel`) return standalone HTML strings +
don't reference dashboard-specific DOM by id. Portable by
construction — no changes needed to host them on the timeline.
The tenant sees the identical action affordance in both places;
one source of truth for how a pending action reads.

**Why prepend, not tab-switch** — I considered adding a status
filter chip that could toggle "pending only" vs "all". Rejected:
adds a mode-selection burden on the tenant, and the pending count
is almost always small (tenants act on follow-ups fast). Prepending
+ auto-hiding when empty is zero-cost when there's nothing pending.

**Why keep the sidebar label short** — `Follow-ups & activity` in
the toolbar reads fine but `Follow-ups & activity` in an 11-char
sidebar entry is cramped. Kept the sidebar at `Follow-ups` (the
primary purpose from a tenant lens), with the hover title carrying
the "+ activity" scope.

## Dogfood (ISO Arion)

Arion currently has 0 pending implications + 0 pending followups
+ 0 overdue followups → "Follow-ups due" section stays hidden.
Timeline renders exactly as before, with the reworded headings.
On a tenant with pending items, the section surfaces at the top
with action buttons; nothing further needed.

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved (SPA-only change).

## Codified lessons

**Lesson 130: A clickable tile promises its destination.** The
Ship 95'.a Dashboard KPI restructure made every tile clickable
with a deep-link. The tiles were labeled by tenant intent
("Follow-ups", "Coverage", "Cite reviews due"). The destinations
had to match that intent to keep the promise. Follow-ups tile said
"actionable things"; destination said "recent history." Broken
promise. Rule: when you make a metric clickable, audit the
destination through the click's mental model — "I clicked because
X; when I arrive, is X still the primary thing I see?"

**Lesson 131: Reuse portable renderers instead of duplicating
patterns.** The Dashboard already had per-implication action
affordance via `renderTriggeredImplicationsPanel`. Rebuilding
that shape on the Cascade timeline would have created two copies
of "how a pending action reads" that would drift the first time
the design changed. Instead: pass the panel HTML string through
to a second host. Rule: when a UI pattern needs to appear in a
second place, check if the existing renderer is portable (returns
HTML string, no host-specific DOM ids). Usually it is. Move it if
not.

**Lesson 132: Rename toolbar titles when the mode's job
changes.** Cascade timeline was originally chronological-only.
Ship 96'.b makes it a two-section mode: actions + activity. The
old title `Cascade timeline` implied "activity only." Left
unchanged, the tenant would still mentally file this mode as
"history view" and miss that they can now act from there. Rule:
when a mode gains a new primary use case, rewrite the toolbar
title + subtitle to lead with the new use case. The subtitle can
still hold the technical detail.

## What's NOT flagged (kept in scope discipline)

- The dashboard's `renderTriggeredImplicationsPanel` still shows
  at the top of the dashboard. Ship 96'.b doesn't remove or
  duplicate it — both places will show pending items until a
  future arc decides one home is enough. Fine to co-exist; the
  dashboard shows-when-non-zero, the timeline shows-when-non-zero,
  the tenant sees action affordance wherever they are.
- No mode-name rename (`m === 'cascade'` still refers to this
  mode internally). Only the tenant-facing labels changed —
  internal identifiers stay stable so hash-routes + notification
  deep-links + code paths all keep working.

## Related

- [[ship-95-prime-a-dashboard-kpi-restructure]] — the arc that
  introduced the clickable Follow-ups tile deep-linking here
- [[ship-96-prime-a-notification-kind-audit]] — sibling arc that
  applied Lesson 124 systematically; this arc applies clickable-
  destination-fidelity checks
- [[dejargonize-ux-pass-2026-07-01]] — the advisory-tone
  vocabulary conventions applied to the toolbar + sidebar renames
- [[feedback-advisory-tone-not-authoritative]] — the tone rule
  applied to the label rewrites
