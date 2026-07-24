---
name: ship-25-prime-arc-retrospective-2026-07-24
description: "Ship 25' arc closer — per-role fanout cap with verdict-first ranking + overflow tail; Art.32 55 → 15 cards; baseline held; role-grouped surface now scales to any fanout"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 25' arc retrospective — 3 sub-arcs across one day
(2026-07-24) closing the UX debt Ship 24's coverage
completion created. Every role section now caps at 8 cards
with verdict-first ranking + an overflow tail. The
role-grouped surface Ship 23'.c delivered can now scale to
any fanout without becoming unusable.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 25'.a | Design memo + cap policy + ranking spec | 07b5002 |
| 25'.b | Backend cap + rank + overflow_counts + prose tail + frontend chip | 51d5464 |
| **25'.c** | **Eval + retrospective (this doc)** | pending |

## The problem Ship 25 solved

Ship 24 completed ISO 27001 cross-role coverage (55.6% →
92.9%). Cross-role cards on high-fanout obligations exploded:

| Query | Pre-Ship-24 | Pre-Ship-25 | **Post-Ship-25** |
|---|---|---|---|
| Art.32 | 26 cards | 55 cards | **15 cards** |
| Art.5  | 25 cards | 45+ cards | **15 cards** |
| A.5.34 | 30 cards | 32 cards | **15 cards** |

The role-grouped surface Ship 23'.c delivered was excellent
UX at 15-30 cards but broke down at 50+. Chat is a triage
surface; the full inventory belongs on the dashboard.

## The design (Ship 25'.a)

**Cap policy**: per-role section cap N=8. Primary card never
capped. Configurable via module-level `_CROSS_ROLE_SECTION_CAP`.

**Ranking key**: `(verdict_severity, -DRAFT_flag, -fanout, ref)`
- Verdict: NC=0 → OFI=1 → Comply=2 → N/A=3 → Unknown=4
- DRAFT flag: draft ranked higher (0 before 1)
- Fanout centrality: cards with more cross-role edges are
  more "central" — tie-breaker after severity + draft
- Ref: alphabetical final tie-breaker

**Overflow tail**: `_Showing 8 of 48 — see all in the
dashboard for <primary_ref>._` with drill-in link to the
existing `/#dashboard?control=X` route.

**Schema addition**: `StructuredAnswer.overflow_counts:
dict = Field(default_factory=dict)` — `{relation: {shown,
total}}` for roles where cap fired. Empty dict when nothing
overflowed. Backend, prose, frontend all consume this signal.

## The implementation (Ship 25'.b)

Three surgical changes:

1. **`answer_augment.py`** — new `_CROSS_ROLE_SECTION_CAP`
   constant + `_VERDICT_SEVERITY` map + `_CAPPABLE_RELATIONS`
   set + `_rank_key(card, fanout_map)` helper. `build_related_
   cards` gains a group→rank→cap pass with `overflow_counts`
   attached to `structured` when a section overflows.
   `structured_to_prose` gains per-section overflow tail with
   sum across relation keys (so `other` section combines
   context + cross_framework_bridge counts).

2. **`answer_schema.py`** — new `overflow_counts` field on
   `StructuredAnswer`. Additive; SDK consumers unaffected.

3. **`arioncomply.html::renderStructuredAnswer`** — section
   defs extended with `relationKeys` tuple. Overflow chip
   emitted when `shownSum > 0 && totalSum > shownSum` for the
   section. New `.sa-overflow` CSS (italic gray-muted with
   purple link).

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to
Ship 15'.e/18'.c/19'.d/20'.e/21'.c/22'.d/23'.c/24'.c
baselines. Zero regression from cap + rank + overflow.

Ship 25 is purely additive: same edges, same primary card,
same first-8 within each section (auditor triage). The tail
signals what's hidden without hiding compliance-load-bearing
data.

## Codified 4 lessons

### 1. Fanout caps are inevitable once coverage is complete

Ship 20-23 argued repeatedly against premature capping ("UI
can scroll") because fanout was modest. Ship 24's completion
made caps unavoidable — Art.32 at 55 cards is genuinely
unusable. Codified property: **any surface that composes from
graph edges will eventually need a cap once the graph is
complete**. Better to design the cap alongside the composition
(as Ship 25'.a did) than to add it as an afterthought.

### 2. Verdict-severity ranking is the auditor's default sort

The rank key `(severity, -DRAFT, -fanout, ref)` puts NC-DRAFT
findings at the top of every capped section. That's what
auditors want: gaps first, settled controls last. This is the
same ordering Stage-2 dashboard uses and matches the
compliance-workflow mental model. Any future capping decision
should default to this same rank.

### 3. Overflow tail is the discipline receipt

Adding `_Showing 8 of 48 — open dashboard →_` isn't just UX
polish. It's the discipline receipt for the retire-visible +
keep-observability idiom: we hide 40 cards from prose but the
tail proves we know they exist. Auditors reading a chat log
can see immediately that data was truncated and where to find
the rest.

### 4. Schema fields for UX signals stay additive

`overflow_counts: dict = Field(default_factory=dict)` doesn't
break existing SDK consumers. It's the fifth `StructuredAnswer`
field after intro/actions/related/risks. Same pattern as
Ship 22'.c's `risks` field — additive, optional, empty by
default. SDK versioning is unnecessary when we stay additive.

## Codified property post-Ship 25

**The role-grouped surface scales to any fanout.** Future
curation arcs (adding SOC 2 CC-series bridges, DORA articles,
NIS2 obligations) will grow the graph but the chat surface
stays visually stable at 15-30 total cards per query. The
top-8-per-role by triage severity remains constant.

Same pattern as Ship 20'.d's Family C 15-cap for short-circuit
stage1/stage2 lists — now extended to the LLM-path
role-grouped surface. Two cap sites, same discipline.

## What Ship 25 did NOT do

- **Per-query-type variable caps.** N=8 uniform. Future arc
  could tune per intent (looser on gap_analysis, tighter on
  definition).
- **New dashboard page for full cross-role listing.**
  Existing `/#dashboard?control=X` drill-in surfaces
  neighbours in context; no need for a new page.
- **Change ranking on other card types.** Risks stay at 8
  (Ship 22'.c) with a different sort (score DESC).
  Templates_block stays uncapped.
- **Retire the prose `answer` field.** Backward compat kept.
- **Change the LLM prompt.** Cap is post-augmentation;
  digest unchanged.

## Ship 25 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 25'.a | Design memo + cap policy + ranking spec | Locked N=8 + verdict-first ranking + overflow tail shape |
| 25'.b | Implementation — schema + backend + prose + frontend | Art.32 55 → 15 cards; verified top-8 Programs all NC-DRAFT; eval 231/232 |
| **25'.c** | **Eval + retro (this)** | **231/232 PASS + 1 WARN + 0 FAIL; arc closed** |

## Related

- [[ship-24-prime-arc-retrospective-2026-07-24]] — the arc
  whose coverage completion made this cap necessary
- [[ship-23-prime-c-role-grouped-surface-2026-07-24]] — the
  role-grouped surface Ship 25 caps
- [[ship-20-prime-d-family-c-2026-07-23]] — Family C 15-cap
  for stage1/stage2 short-circuits (same discipline)
- [[ship-22-prime-c-riskcard-retire-2026-07-24]] — RiskCard's
  own 8-cap (top-N by risk_score DESC)
