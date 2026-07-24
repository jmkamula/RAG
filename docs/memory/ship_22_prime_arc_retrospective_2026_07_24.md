---
name: ship-22-prime-arc-retrospective-2026-07-24
description: "Ship 22' arc closer — retired bridge + risk prose footers; added RiskCard schema + demonstrator auto-inject; every prose footer now retired; 231/232 baseline held after widened demonstrator injection closed 2 cross-framework regressions"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 22' arc retrospective — 4 sub-arcs across one day
(2026-07-24) finishing the chat prose cleanup started in Ship
18. All three prose footers (`↳ Compliance facts:`,
`↳ Bridges to ISO 27001 ...`, `↳ Risk register: R-...`) are now
retired. Every equivalent piece of information lives in the
structured payload cards + the `## Related controls` / `## Risks`
prose sections.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 22'.a | Design memo + eval coverage grep + audit-trail plan | 539670d |
| 22'.b | Bridge footer retirement (no schema change) | dd5791d |
| 22'.c | RiskCard schema + `risks: list[RiskCard]` + `## Risks` prose section + risk footer retirement + frontend renderer | d1a4a44 |
| **22'.d** | **Demonstrator auto-inject + eval + retrospective (this doc)** | pending |

## Auditor-trail guarantee (blowback prevention)

Same discipline as Ship 21: retire visible surface, preserve
observability path.

- Repair events (`missing_bridge_footer`, `missing_risk_ref`)
  still fire in `check_and_repair`; only the visible prose
  appends removed.
- `chat_casefile_log.repair_events` continues to populate.
- `scripts/audit_retired_footer.sql` header comment extended to
  document all 3 retired footers (Ship 21'.b + 22'.b + 22'.c)
  + all event kinds the query surfaces. Same auditor query;
  wider coverage.

## Eval outcome + Ship 22'.d salvage

| Baseline | 22'.d run 1 | 22'.d run 2 | **22'.d run 3 (final)** |
|---|---|---|---|
| PASS | 231/232 | 230/232 | 230/232 | **231/232** |
| WARN | 1 (#200) | 1 (#200) | 1 (#200) | **1 (#200)** |
| FAIL | 0 | 1 (#25) | 1 (#24) | **0** |

**Run 1** failed case #25 (`is GDPR Art.5 a non-conformity?`
— `xfw_shape: no ISO bridge ref found`). Root cause: LLM cited
only GDPR refs (Art.5, Art.5.1.a, Art.5.1.f); no ISO bridges
appeared in `## Related controls`. Before Ship 22'.b the
retired `↳ Bridges to ISO 27001 for Art.5:` footer would have
listed A.5.33 etc.

**Fix (first pass)**: extend `build_related_cards` to
auto-inject `_collect_demonstrators(cf, primary_ref)` as
extra_refs. Run 2 confirmed #25 passes.

**Run 2** failed case #24 (`what is our GDPR Art.32 status?`
— same xfw_shape error). Root cause: LLM cited a sub-article
first (Art.32.1.d), so `primary_ref = "Art.32.1.d"`. The
`demonstrated_by` overlay lives on `Art.32`, not on the
sub-article. `_collect_demonstrators("Art.32.1.d")` returned
empty set.

**Fix (final)**: widen the injection to run
`_collect_demonstrators` over EVERY cited ref, unioning all
demonstrators. Mirrors what the retired bridge footer did
(iterated all cited article refs). Run 3 confirmed baseline
restored.

## Codified pattern: demonstrator auto-inject

Retiring a footer that had preservation-check semantics needs
more than removing the append line. The bridge footer served
TWO roles:

1. **Visible surface** — showing the tenant the bridge refs.
   Card render + `## Related controls` covers this.
2. **Preservation guarantee** — ensuring cross-framework refs
   ALWAYS appear regardless of LLM whim. This was silent —
   easy to miss when retiring.

Ship 22'.d added the preservation guarantee at the augment
layer:
- Iterate every cited ref
- For each, union in `demonstrated_by` sources
- Add all demonstrators as `extra_refs` to
  `build_related_cards`

Now the invariant holds structurally, not via prose repair.

Two lessons:
- **Retire-visible + keep-observability is necessary but not
  sufficient.** Ship 21 pattern was clean because the
  compliance-facts footer only had role #1 (visible surface).
  Bridge footer had roles #1 AND #2; retirement needed to move
  #2 to a structural invariant.
- **When retiring a footer, ask "what happens if the LLM says
  nothing about the topic that footer covered?"** If cards
  still render → clean retirement. If cards go empty →
  preservation logic needs to move upstream.

## New: RiskCard as a first-class type

Prior to Ship 22, risks lived in a `↳ Risk register: R-...`
prose footer + a heavier `renderRisks` UI in a separate mode.
The chat surface had no card-level risk representation.

Ship 22'.c added:
- `RiskCard` Pydantic model — 11 fields including
  external_ref, threat, risk_score, treatment_status,
  linked_controls[], dashboard_url
- `StructuredAnswer.risks: list[RiskCard]` — parallel array
  alongside `related[]` (risks aren't controls so squeezing
  into RelatedCard would have distorted semantics)
- `build_risk_cards(risks_data)` helper — deterministic
  dict→RiskCard conversion; sorts linked_controls by role
  (program → extension → obligation)
- `structured_to_prose` gains `## Risks` section (bold ref +
  threat + score/25 + treatment + linked refs, with `+N more`
  overflow)
- Frontend renderer: red left border matching NC color; score
  badge + treatment chip + linked-controls ref tags + "Open
  risk register →" drill-in via existing `/#risks` mode

Populated automatically for posture_risk turns:
- LLM path: via `augment_and_repair` reading `cf.risks`
- Risk short-circuit: passes `risks_data =
  fetch_risks_for_casefile(_tid, top_n=8)` to
  `build_short_circuit_structured`

## Codified properties post-Ship 22

- **All three prose footers retired.** `↳ Compliance facts:`
  (Ship 21'.b), `↳ Bridges to ISO 27001:` (Ship 22'.b),
  `↳ Risk register:` (Ship 22'.c). No prose footer remains.
- **Preservation guarantees are STRUCTURAL, not textual.**
  Demonstrators auto-inject at card-build time; risks
  auto-attach from CaseFile.risks. LLM whim can't drop
  bridge/risk information.
- **RiskCard is the fourth card type** (alongside IntroCard,
  ActionCard, RelatedCard). Same deterministic-augmentation
  discipline as RelatedCard.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — RelatedCard.role preserved; RiskCard.linked_controls sorted by role. |
| Parallel CaseFile view? | YES — same CaseFile drives all augmentation. |
| Deterministic routing? | YES — Ship 22 is prose-composition + augmentation only. |
| Guidance-normative discipline? | YES — cards carry role; risk-linked controls preserve role ordering. |

## What Ship 22 did NOT do

- **Retire the prose `answer` field itself.** Backward compat.
- **Retire `PreservationSpec.bridge_footer` /
  `required_risk_refs` fields.** Still gate the repair-event
  firing (kept for audit log).
- **Cap the related-card count on cross-framework queries.**
  Art.5 auto-injection produced 21 demonstrator cards.
  Uncapped is what the retired bridge footer also did; UI
  can scroll. Cap decision deferred.
- **Migrate the risk short-circuit to Family C.** Stays
  Family A (intro-only prose from `polish_short_circuit_answer`)
  + parallel `risks[]` metadata for the card render.

## Lessons

1. **Retire-visible + keep-observability is necessary but not
   sufficient.** The Ship 21 pattern generalizes cleanly only
   when the footer's sole role was visible surface. Bridge
   footer had a hidden preservation-guarantee role; retirement
   had to encode that as a structural invariant (demonstrator
   auto-inject).

2. **Widen the invariant on the first regression.** Run 1's
   fix (`primary_ref`-only demonstrators) worked for Art.5
   but not Art.32 because the LLM primed on a sub-article.
   Run 2's fix (all cited refs) is broader by design — mirrors
   the retired footer's own iteration pattern. Every cited
   article contributes; no ordering dependency.

3. **The old footer's iteration logic was a spec, not just an
   implementation.** `_build_bridge_footer` iterated
   `_extract_article_refs(cf)` — a set of all article refs
   in cited + query text. Ship 22'.d's `for ref in list(cited)`
   loop reconstructs the same set at augment time. Reading
   the retired code as a spec surfaced the correct invariant
   quickly.

4. **Sub-article ref inheritance is a real pattern.** Multiple
   posture surfaces (bridges, evidence propagation) depend on
   article-level metadata that sub-articles inherit. A
   catalog-side redesign that materializes sub-article
   demonstrators would eliminate a class of these fixes; not
   in Ship 22 scope but noted for future arcs.

## Ship 22 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 22'.a | Design + eval-coverage grep + audit-SQL doc | Locked full-retirement + RiskCard shape |
| 22'.b | Bridge footer retirement | Prose cleaned; cards fully cover for typical queries |
| 22'.c | RiskCard + risk footer retirement + frontend | Fourth card type shipped; last prose footer gone |
| **22'.d** | **Demonstrator auto-inject + eval + retro (this)** | **231/232 restored; preservation invariant now structural** |

## Related

- [[ship-21-prime-arc-retrospective-2026-07-23]] — the arc
  whose retire-visible + keep-observability pattern this arc
  extends and expands
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — the risk
  feature this arc extends with card rendering
- [[ship-1-14-bridge-footer]] (see
  `cross_framework_bridge_footer_2026_06_14`) — the original
  bridge footer this arc retires
- [[cross-framework-bridge-footer-2026-06-14]] — the source
  memo whose invariant Ship 22'.d encodes structurally
