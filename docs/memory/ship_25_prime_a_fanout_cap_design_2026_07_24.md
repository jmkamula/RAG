---
name: ship-25-prime-a-fanout-cap-design-2026-07-24
description: "Ship 25'.a — design memo for per-role fanout cap on cross-role cards; ranks by verdict severity + draft + fanout; overflow tail 'showing N of M — open dashboard'"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 25'.a — opens Ship 25 arc (fanout cap). Post-Ship-24
completion, Art.32 obligation query surfaces 55 cross-role
cards (48 Programs alone). The role-grouped surface Ship 23'.c
delivered is now genuinely unusable on high-fanout obligations
+ broad programs. Ship 25 caps per-role sections without
sacrificing information.

## The problem

Art.32 (Security of processing) has the largest fanout after
Ship 24's completion because so many ISO 27001 controls
demonstrate its TOM requirements. Similar issue on Art.5
(Principles) and Art.24 (Controller accountability).

Card count on Art.32 (post-Ship-24):
- Primary: 1
- Programs: 48 (up from 22 pre-Ship-24)
- Extensions: 4
- Context: 2
- **Total: 55 cards** — unusably long chat message

Rendering 55 cards blows past the "auditor triage surface"
purpose of the chat card render. Dashboard is where full
inventory belongs; chat is for the top few relevant items.

## The plan

### Cap policy

Per-role section cap: **N = 8** cards per role section.
Configurable via module-level constant. Applied to related
cards only; primary card always shown regardless.

Sections covered by the cap:
- `program` — Programs
- `extension` — Extensions
- `obligation` — Obligations
- `isms_clause` — Management-system clauses
- `context` — Related controls (fallback bucket)

Not capped:
- `primary` — always 1 card, always shown
- `risks` — separate top-level; Ship 22'.c already caps at 8

### Ranking

When we cap at N, which N do we keep? Rank by (highest priority first):

1. **Verdict severity** — NC > OFI > Comply > N/A > Unknown.
   Auditor cares about gaps first; a tenant with 40 Programs
   demonstrating Art.32 mostly wants to see the ones with
   NC findings.
2. **DRAFT flag** — DRAFT ranked higher than confirmed.
   Draft findings need attention; confirmed states are
   settled.
3. **Fanout centrality** — cards with more cross-role edges
   are more "central" to the tenant's compliance posture.
   Tie-breaker after severity + draft.
4. **Ref (alphabetical)** — deterministic final tie-breaker.

Ranking key: `(severity_bucket, -draft_flag, -fanout, ref)`.

### Overflow affordance

When a section has more cards than the cap, emit an overflow
tail:

**Prose** (`structured_to_prose`):
```markdown
## Programs
- **A.5.15** ...
- **A.5.18** ...
- ... 8 cards shown ...

_Showing 8 of 48. See all in the dashboard._
```

**Frontend** (`renderStructuredAnswer`):
```html
<div class="sa-overflow">
  Showing 8 of 48 —
  <a href="/#dashboard?control=Art.32" onclick="setMode('dashboard');return true;">
    open dashboard →
  </a>
</div>
```

Drill-in target: `/#dashboard?control=<primary_ref>` — the
dashboard drill-in for the primary already shows related
controls in context. No new dashboard page needed.

### Cap is opt-in / configurable

Module-level constant `_CROSS_ROLE_SECTION_CAP = 8`. Future
arcs can adjust or replace with a per-query heuristic (e.g.
cap tighter on definition queries, looser on gap_analysis).

### What the ranking preserves

For an obligation like Art.32:
- Top 8 Programs will always include the NC-DRAFT ones
  (auditor's action items)
- OFI-DRAFT + high-fanout programs come next (e.g. A.5.15,
  A.8.24 which are core Art.32 anchors)
- Comply / N/A ranked last (already settled)

For a program query like A.5.34:
- Top 8 Extensions will include the NC-DRAFT ones
- All 21 extensions available in the dashboard drill-in

The tenant's day-to-day workflow (what needs remediation)
stays at the top; the completeness view moves to the
dashboard.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | REINFORCED — cap is per-role-section; each role gets its own cap window. Programs section might have 48 total but 8 shown; Extensions might have 4 total, all shown. |
| Parallel CaseFile view? | YES — no digest changes; ranking + cap happen in `build_related_cards` post-augmentation. |
| Deterministic routing? | YES — ranking is deterministic (verdict → draft → fanout → ref). |
| Guidance-normative discipline? | YES — DRAFT ranking preserves the "unconfirmed needs attention" hierarchy. |

## Alternative approaches considered + rejected

1. **Show all, let UI scroll.** Chat message becomes 55-card
   scroll fest; buries the intro + actions. Rejected.

2. **Cap in the frontend only.** Backend still emits 55 cards.
   Data cost on the wire + SDK consumers hit the same
   problem. Reject; cap belongs in `build_related_cards`.

3. **Prompt the LLM to summarise the section.** Structural
   metadata should never come from an LLM emission per Ship
   22-23 codified property. Reject.

4. **Group cards by verdict within each section.** Adds
   visual complexity; caller can already ORDER cards by
   verdict without adding sub-groupings. Reject.

## Sub-arc plan

### 25'.b — Implement

- `rag/casefile/answer_augment.py`:
  * new `_rank_key(card)` returning `(severity, -draft,
    -fanout, ref)`
  * new `_CROSS_ROLE_SECTION_CAP = 8` constant
  * post-augmentation pass in `build_related_cards`: group
    by relation, rank each group, cap at N, track
    `overflow_count` per role
  * new `StructuredAnswer.overflow_counts: dict[str, dict]`
    field carrying `{role: {shown: int, total: int}}` for the
    frontend + prose
- `rag/casefile/answer_schema.py`: add `overflow_counts` field
- `rag/casefile/answer_augment.py::structured_to_prose`:
  emit `_Showing N of M — see all in the dashboard._` tail
  in overflown sections
- `static/arioncomply.html::renderStructuredAnswer`:
  overflow chip with drill-in to `/#dashboard?control=X`

### 25'.c — Eval + retro

Same discipline as prior arcs.

## Design decisions locked in 25'.a

1. **N=8 per role section.** Small enough to fit visually,
   large enough to convey pattern. Adjustable via constant.

2. **Verdict-severity-first ranking.** Auditor triage
   surface — NC/OFI/DRAFT first, Comply/N/A last.

3. **Primary always shown.** Never cap the primary card;
   it's the auditor's own query focus.

4. **Overflow drill-in to primary's dashboard entry.** No
   new dashboard page needed; the drill-in of the queried
   control already surfaces related controls.

5. **Cap in backend, not frontend.** Data cost + SDK parity.
   Frontend just renders what backend delivers.

6. **Track shown/total per role in structured payload.**
   Frontend + prose need this to render the overflow tail.
   SDK consumers get it too — API consistency.

## What Ship 25 does NOT do

- **Per-query-type variable caps.** N=8 uniform. Future arc
  could tune per intent.
- **Add a new dashboard page** for full cross-role listing.
  Existing drill-in surfaces neighbours already.
- **Change the LLM prompt.** Card cap is post-augmentation;
  LLM sees the same digest.
- **Cap on non-obligation queries.** Cap applies uniformly;
  program/extension queries also cap Programs section if
  they somehow had 8+ related programs (rare).
- **Retire the Related section fallback.** `context` bucket
  still catches un-classified cards; capped like the others.

## Ship 25 progress

| Sub-arc | Status |
|---|---|
| **25'.a Design memo (this)** | **✓** |
| 25'.b Implement cap + rank + overflow | next |
| 25'.c Eval + retro | pending |

## Related

- [[ship-24-prime-arc-retrospective-2026-07-24]] — the arc
  whose coverage completion made this cap necessary
- [[ship-23-prime-c-role-grouped-surface-2026-07-24]] — the
  role-grouped surface Ship 25 caps
- [[ship-20-prime-arc-retrospective-2026-07-23]] — Family C
  cap pattern (stage1/stage2 15-cap) that inspired this
