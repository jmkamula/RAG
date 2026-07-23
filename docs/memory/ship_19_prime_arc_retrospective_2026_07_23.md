---
name: ship-19-prime-arc-retrospective-2026-07-23
description: "Ship 19' arc closer — chat card polish (per-leaf checklist on primary card + intro dedupe + intro rule refinement); 231/232 baseline restored after 4 JSON-mode prompt-rule regressions closed"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 19' arc retrospective — 4 sub-arcs across one day
(2026-07-23) delivering chat card polish following the Ship 18
structured payload landing. Origin: user tested the Ship 18 UI
and flagged 3 concrete usability issues on "how do I remediate
A.5.15?".

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 19'.a | Design memo (per-leaf checklist on primary card; intro dedupe; prompt tweak) | c433d63 |
| 19'.b | Backend `RelatedCard.leaves[]` + LLM output rule extension | 916519f |
| 19'.c | Frontend checklist render + intro chip dedupe + CSS | 62eb419 |
| **19'.d** | **Rule 1 + rule 7 refinement + eval + retrospective (this doc)** | pending |

## The 3 user-flagged issues → fixes

Test query: "how do I remediate A.5.15?" against the Ship 18 UI.

| Issue | Fix |
|---|---|
| Intro shows `[A.5.15]` chip + then text "ISO 27001 A.5.15..." — double-mention | Frontend skips chip when `intro.text` leads with the ref (within first 40 chars) |
| Card shows `still_needed` chips but not the fulfilled items | New `RelatedCard.leaves[]` array with per-leaf `satisfied` state; frontend renders ✓/○ checklist on primary card |
| Intro "1 of 4 items present" is vague duplication of card content | New LLM output rule: intro must NOT restate N-of-M count (checklist owns the enumeration) |

## Verified end-to-end on "how do I remediate A.5.15?"

Before:
```
[A.5.15] ISO 27001 A.5.15 (Access control) requires... OFI-DRAFT
with only 1 of 4 required items present.

... [3 action cards, no fulfilled/missing enumeration] ...

↳ Compliance facts: 10.1 [NC-DRAFT] — ALL: 0 of 4 required items
  present ...; still needed: operating procedure, sc…
```

After:
```
ISO 27001 A.5.15 (Access control) requires ensuring authorized
access... Currently OFI-DRAFT.

... [3 action cards with concrete guidance] ...

A.5.15 [OFI-DRAFT] Primary control
  ✓ Management Approval    (3/3 items)
  ○ Access Control Policy  (5/6 items)
  ○ Communication Record   (1/5 items)
  ○ Periodic Review        (1/5 items)
```

## Eval outcome

| Baseline | Before | Ship 19'.b initial | **Ship 19'.d final** |
|---|---|---|---|
| PASS | 231/232 | 227/232 | **231/232** |
| WARN | 1 (#200) | 1 (#200) | **1 (#200)** |
| FAIL | 0 | 4 | **0** |

Ship 19'.b's new prompt rule ("intro must not restate N-of-M
count") over-generalized in JSON mode; the LLM interpreted it as
"make intro tighter across the board" and dropped:
- **#3** "OFI" acronym on `show me our OFI findings` (used
  "opportunities for improvement" but dropped the acronym)
- **#10** "certif" framing entirely on `are we certified?`
  (answered posture status without addressing certification)
- **#223** "27003" on `what does ISO 27003 say about ISMS
  management review?`
- **#224** "27004" on `what does ISO 27004 say about monitoring
  and measurement?`

Same failure mode as Ship 18'.b: JSON mode compresses; subtractive
prompt rules propagate beyond their intended scope. Closed in
19'.d by:

1. **Rule 1 restructured** — Made explicit that the N-of-M drop
   is THE ONLY subtractive rule. Added positive constraint:
   intro MUST echo the query's key terms. Added a 3-example
   pattern showing the shape for (a) single-control queries,
   (b) meta-questions like "are we certified?", and
   (c) guidance-standard queries.

2. **Rule 7 reinforced** — Added a "regardless of brevity"
   clause + explicit query-echo: "when the query names an ISO
   standard, the intro MUST echo that standard's name."

Post-fix eval: 231/232 PASS + 1 WARN (#200 pre-existing) + 0 FAIL
— identical to Ship 15'.e and Ship 18'.c baselines.

## Design decisions locked in

1. **Primary card owns the leaf-level scorecard.** User picked
   per-leaf granularity over per-MUST detail (offered as an
   option). Simpler UX; matches auditor mental model.

2. **`leaves[]` populated on every card, rendered only on
   primary.** Backend is uniform; frontend controls render
   granularity. Non-primary cards (ISMS clauses, cross-framework
   bridges, demonstrated-by) keep the compact still_needed chip
   surface — otherwise a typical remediation query would render
   4× the visual weight.

3. **Fallback to still_needed chips when leaves[] is empty.**
   Controls without advisory data (single-leaf, Comply, N/A) or
   errors in `build_per_must_advisory_data` render the old chip
   surface. No regression.

4. **APPEND-ONLY preservation preserved.** `leaves[]` derives
   from posture, not from LLM output. Same discipline as Ship 18.

5. **Chip dedupe on frontend, not backend.** Backend keeps
   `intro.primary_ref` for API/SDK consumers who render prose.
   Frontend decides not to render the chip when the ref is
   already prominent in the text.

## Codified properties post-Ship 19

- **Primary card is the tenant's leaf-level scorecard.** Every
  remediation-shaped chat answer shows a ✓/○ checklist on the
  primary control with real leaf titles + per-MUST counts. No
  more "1 of 4 required items present" — the checklist tells the
  tenant exactly WHICH items.

- **Subtractive prompt rules must be narrowly scoped.** Any
  "don't do X in Y" rule risks the LLM over-generalizing in JSON
  mode. Codified pattern: pair subtractive rule with explicit
  positive constraint AND multiple examples covering the
  varieties of query shape.

- **Ship 18 + Ship 19 together form the case-file arc's card
  rendering layer.** Ship 18 built the structured payload +
  card render primitives. Ship 19 populated per-leaf detail +
  cleaned up visual redundancy. This is the current chat UX
  baseline.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — leaves inherit their control's role via `RelatedCard.role`; guidance-role controls typically render empty checklist (no evidence expectations) correctly. |
| Parallel CaseFile view? | YES — checklist data flows from `build_per_must_advisory_data` which shares the CaseFile's role model. |
| Deterministic routing? | N/A — presentation-layer arc. |
| Guidance-normative discipline? | YES — Rule 7 explicitly reinforces that guidance-standard names must appear in intro regardless of brevity constraints. |

## What Ship 19 did NOT do

- **Per-MUST expansion under leaves** — deferred (offered as an
  option, user picked leaf-level only). Per-MUST detail stays
  in the Stage-1 detail panel and dashboard drill-in.
- **Change non-primary card rendering** — related cards stay
  compact. Full checklist on every card would quadruple visual
  weight.
- **Progress bars / percentage rings** — check icons carry the
  state; progress bars add visual weight without new info.
- **Migrate other query surfaces (definition, listing)** — the
  primary-card checklist applies to remediation/gap-analysis
  queries. Definition queries have empty actions[] by design; no
  primary card to check-list.

## Lessons

1. **Two hard-earned lessons about subtractive prompt rules in
   JSON mode:**
   - **Ship 18'.b** — "compress inline" got over-generalized;
     LLM dropped bulleted enumerations + guidance-standard names.
     Fixed with explicit rules 7 + 8 that positively required
     what was disappearing.
   - **Ship 19'.b** — "don't restate N-of-M" got over-generalized;
     LLM dropped query-echo terms + guidance-standard names
     (again, despite rule 7 existing). Fixed by restructuring
     rule 1 to state that N-of-M is the ONLY subtractive rule
     AND adding a positive query-echo constraint.

   Meta-lesson: **every subtractive prompt rule needs a paired
   positive constraint that says "everything else stays".**
   Otherwise the LLM will treat the subtractive rule as a
   general "be tighter" signal in JSON mode.

2. **Examples in prompt rules do heavy lifting.** Rule 1's
   3-example pattern (single-control / meta-query /
   guidance-standard) demonstrably closed the 4 regressions
   where an abstract instruction had failed. Pattern:
   whenever a rule can apply to N shapes of query, give N
   examples in the prompt.

3. **User feedback → concrete arc plan → 4 sub-arcs → shipped
   in one day.** The user tested Ship 18 and gave 3 concrete
   issues; the arc opened with a fully-specified fix (not
   abstract options) and closed in the same day. Contrast with
   arcs that open with hypothetical improvements — those tend
   to sprawl.

4. **Data derivation over LLM structured emit — the pattern
   compounds.** Ship 18 established: LLM emits intro + actions,
   backend builds related. Ship 19 extended: backend also builds
   leaves[] (deterministic from posture). Every field that has a
   canonical source is derived; every field that requires
   narrative is LLM-emitted. This is the current idiom for
   compliance-load-bearing outputs.

## Ship 19 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 19'.a | Design memo — primary-card checklist strategy | Locked leaf-level-only granularity + intro dedupe approach |
| 19'.b | Backend leaves[] + LLM rule extension | Backend delivered; initial eval 227/232 (4 regressions) |
| 19'.c | Frontend checklist + intro dedupe + CSS | UI rendered correctly on live tenant; regressions unchanged |
| **19'.d** | **Rule 1 restructure + rule 7 reinforcement + eval + retro (this)** | **231/232 baseline restored — arc closed** |

## Related

- [[ship-18-prime-arc-retrospective-2026-07-23]] — the arc whose
  UI Ship 19 polished
- [[ship-18-prime-c-frontend-cards-prompt-rules-2026-07-23]] —
  precedent for JSON-mode prompt-rule regressions +
  positive-constraint fixes
- [[ship-19-prime-a-card-polish-design-2026-07-23]] — design memo
- [[framework-role-model-arc]] — role model that primary/related
  card distinction reflects
- [[feedback-anchor-before-choices]] — user gave concrete UI
  feedback; arc opened with concrete plan not abstract options
