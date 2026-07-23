---
name: ship-20-prime-arc-retrospective-2026-07-23
description: "Ship 20' arc closer — extended Ship 18 structured payload to all 13 short-circuit paths in arion_graph.py via CaseFileShim + 3-family per-site migration; 231/232 baseline held, zero regression across 4 sub-arcs"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 20' arc retrospective — 5 sub-arcs across one day
(2026-07-23) extending the Ship 18/19 structured chat response
to every short-circuit path in `arion_graph.py`. Before Ship 20:
only the LLM/case-file path emitted `answer_structured`;
deterministic short-circuits (timeline, cascade, stage1, stage2,
posture_enumeration, etc.) returned prose only. After Ship 20:
every chat path emits a structured payload.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 20'.a | Design memo + 15-site inventory + 3-family classification | 9846eb6 |
| 20'.b | Family A intro-only helper + 7 no-refs sites wired | 96031b8 |
| 20'.c | CaseFileShim + fetch_control_metadata + Family B (3 sites, intro+1 related) | db9554f |
| 20'.d | Family C (3 sites, intro+N capped 15) + cap-bug fix | 14e747e |
| **20'.e** | **Eval + retrospective (this doc)** | pending |

## Site inventory: 15 sites, 3 card-shape families

| Family | Sites | Card shape |
|---|---|---|
| A (intro-only) | deictic_clarify, scope_na, cascade_followups, risk, cascade_suppressions, upload_status, resolver_short_circuit | Intro bubble; actions=[], related=[] |
| B (intro + 1 related) | acknowledge_gap, cascade_implications, timeline | Intro + 1 primary card |
| C (intro + N related, capped 15) | stage1_review, stage2_approval, posture_enumeration | Intro + up to 15 related cards |

## Shared infrastructure

### CaseFileShim (`answer_augment.py`)

Duck-typed stand-in for CaseFile so `build_related_cards` works
without a full CaseFile (which the LLM path builds via
SimpleNamespace at rank_and_answer:1132; short-circuits don't
have the resolver outputs). Constructor takes `tenant` +
`posture_by_ref` + optional `node_lookup`. Duck-types the 5
methods `build_related_cards` needs: `all_nodes`, `posture_for`,
`needs_draft_tag`, `role_of`, `demonstrated_by`.

### fetch_control_metadata (`answer_augment.py`)

Batch Neo4j query returning `{ref: {title, standard_id}}` for
a set of refs. Uses `rn.ref` (initial guess `rn.control_ref`
was wrong — corrected after Family B smoke test showed empty
titles). Fails silently → returns partial or empty dict.

### build_short_circuit_structured (`answer_augment.py`)

Family B/C builder. Takes intro_text + primary_ref + extra_refs
+ tenant + posture_by_node_id + tenant_id. Opens its own
short-lived pg connection for advisory data (leaves/still_needed/
evidence_summary) — mirrors the LLM-path augment flow. Passes an
EMPTY intro.text to build_related_cards during augmentation (see
"Bug fix during Family C" below) then restores the real intro.

### build_intro_only_structured (`answer_augment.py`)

Family A helper. Trivial: returns StructuredAnswer with
`intro=IntroCard(text=..., primary_ref=...)`, `actions=[]`,
`related=[]`.

## Eval outcome

| Baseline | 20'.a | 20'.b | 20'.c | 20'.d | 20'.e |
|---|---|---|---|---|---|
| PASS | 231/232 (unchanged) | (unchanged) | (unchanged) | (unchanged) | **231/232** |
| WARN | 1 (#200) | (unchanged) | (unchanged) | (unchanged) | **1 (#200)** |
| FAIL | 0 | 0 | 0 | 0 | **0** |

Zero regression across all 4 delivery sub-arcs. Same baseline as
Ship 15'.e / 18'.c / 19'.d. Only remaining WARN is #200
(posture_check vs gap_analysis mismatch documented in CLAUDE.md
as pre-existing).

Ship 20 added ONLY the `answer_structured` field — never modified
`answer_text` prose. Eval assertions scan `answer_text`, so the
zero-regression outcome was expected but proven.

## Bug fix during Family C

First Ship 20'.d smoke test on `show pending findings`:
returned 34 related cards instead of the coded 15-cap. Root
cause: `build_related_cards()` calls
`collect_all_refs(structured)` which scans `intro.text +
actions[].body` for refs. The Stage-1 `render_stage1_answer`
prose mentions 42 pending controls by ref — scan picked all up,
unioned with the caller's `extra_refs` (15), produced 34 unique
after Neo4j filter.

Fix: pass EMPTY `intro.text` to `build_related_cards` during
the short-circuit augment; restore the real intro after. Short-
circuits are authoritative about which refs to surface (caller
knows via `_s1_listing[:15]`); the LLM path is not (LLM prose IS
the source of cited refs). One-line change in
`build_short_circuit_structured`; preserves LLM path behaviour.

## Design decisions locked in

1. **CaseFileShim over SimpleNamespace boilerplate.** Reusable
   duck-typed helper; one construction per short-circuit; keeps
   `build_related_cards` signature unchanged so LLM path is
   untouched.

2. **Intro-only IS a legit structured shape.** Not every response
   needs cards; consistency of envelope matters more than
   forcing multi-card layout on clarifications / no-refs
   summaries.

3. **Cap Family C enumeration at 15 refs.** 30+ cards would
   overwhelm the chat surface. Prose intro carries the full
   count summary; drill-in to dashboard for the full list.

4. **Short-circuits DO NOT get JSON-mode LLM.** Existing
   `polish_short_circuit_answer` prose call stays; we wrap its
   output as `intro.text` rather than replace it.

5. **Empty intro.text during ref scan** — short-circuits are
   authoritative about their refs; the LLM path is not. This
   asymmetry justifies the per-path behavior.

6. **`answer_text` composed same way everywhere.** Backward
   compat for SDK / prose consumers. `answer_structured` is
   parallel; frontend prefers cards when present.

7. **`attach_templates` / `attach_advisory` defaults unchanged.**
   Ship 20 doesn't touch what the envelope currently attaches
   per site.

## Codified properties post-Ship 20

- **Every chat path emits `answer_structured`.** Consistent
  envelope across the entire chat surface — clients no longer
  branch on structured absence for the deterministic paths.
- **Structural metadata is deterministic on every path.**
  Role/verdict/relation/evidence_summary/leaves come from
  Postgres + Neo4j on EVERY path (LLM path via CaseFile, short-
  circuits via CaseFileShim). No compliance-load-bearing data
  ever comes from an LLM emission.
- **Ship 18 + 19 + 20 form the complete card-based chat UX.**
  Ship 18 built the primitives + LLM path. Ship 19 polished the
  render (per-leaf checklist, intro dedupe, prompt rules).
  Ship 20 extended to every short-circuit. The card render is
  now the default across all chat surfaces.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — every card carries `role` first-class via CaseFileShim or CaseFile. |
| Parallel CaseFile view? | N/A for short-circuits (they don't have LLM turns to preserve). Preserved on LLM path. |
| Deterministic routing? | YES — every short-circuit already deterministic; Ship 20 preserved that. |
| Guidance-normative discipline? | YES — cards carry role; guidance-role controls (rare in short-circuits) render distinguishably. |

## What Ship 20 did NOT do

- **Change LLM path.** It already emits structured; no changes.
- **Redesign risk cards.** Risk short-circuit gets Family A
  intro-only; the richer risk visualization (`renderRisks` /
  `showRiskDetail`) elsewhere in the UI stays.
- **Retire `polish_short_circuit_answer`.** Prose polish call in
  postgres+llm sites stays; wrapped as intro.text.
- **Backfill historical `chat_casefile_log` rows.** Only the
  case-file (LLM) flow logs there. Short-circuits don't touch
  the log; Ship 20 doesn't add new logging paths.
- **Frontend changes.** Ship 18/19 renderer handles Family A/B/C
  payloads identically to the LLM path. Zero frontend commits
  needed in this arc.
- **New eval cases.** No prompt or classifier changes; the
  existing 232-case baseline is the regression signal.

## Lessons

1. **Duck-typing over refactor.** `CaseFileShim` gave 3 short-
   circuit families access to `build_related_cards` without
   touching the LLM path or the shared function's signature.
   ~50 LOC helper + zero downstream ripple. Preferable to a
   parameter-refactor when the code path is already stable.

2. **Empty-input scanning as a discipline signal.** The
   Family C bug (34 cards from a 15-cap) surfaced a real
   architectural asymmetry: LLM path treats prose as authoritative
   for ref-set (because LLM chose them); short-circuit path
   treats prose as descriptive (caller chose the refs).
   Passing empty intro.text during scan encodes this asymmetry
   cleanly.

3. **Per-site over auto-derive was the right call.** User picked
   per-site early in the arc. Family A/B/C classification let
   me batch similar sites; each family's wiring was mechanical
   after the first site. Total: 13 sites × ~10 LOC each = ~130
   LOC of graph-side changes. Auto-derive would have been ~30
   LOC but every site would have needed some override logic to
   handle its query-specific data shape — probably net-neutral
   on LOC but harder to reason about per-site.

4. **Neo4j property discipline pays.** Ship 20'.c's first Family
   B smoke test showed `title=""` because I queried
   `rn.control_ref` instead of `rn.ref`. Quick fix; but a
   reminder that graph-schema divergence bites at query time.
   Follow-up: add a rag/id_types.py-style validator for graph
   property names.

## Ship 20 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 20'.a | Design memo + 15-site inventory + family classification | Locked per-site path + CaseFileShim approach |
| 20'.b | Family A: intro-only helper + 7 no-refs sites | All 7 sites emit intro-only structured; frontend renders correctly |
| 20'.c | CaseFileShim + Neo4j fetch + Family B (3 sites) | Full Family B cards with title + leaves; Neo4j property bug found + fixed |
| 20'.d | Family C (3 sites) + cap-bug fix | 15-card cap enforced via empty-intro-scan; every path now emits structured |
| **20'.e** | **Eval + retrospective (this doc)** | **231/232 PASS + 1 WARN + 0 FAIL — arc closed** |

## Related

- [[ship-18-prime-arc-retrospective-2026-07-23]] — the LLM-path
  structured payload arc Ship 20 extended
- [[ship-19-prime-arc-retrospective-2026-07-23]] — the card
  polish arc providing the render Ship 20 feeds into
- [[ship-20-prime-a-short-circuit-design-2026-07-23]] — design
- [[framework-role-model-arc]] — role model that CaseFileShim
  preserves via `tenant.scope` role_map lookup
- [[dejargonize-ux-pass-2026-07-01]] — consistency-across-
  surfaces principle Ship 20 completed for the chat surface
