---
name: case-24-art32-bridge-followup
description: "RESOLVED 2026-06-14 — eval #24 + #25 stabilised via shape='cross_framework' validator (b293e8d) + deterministic bridge footer in llm_answer.rank_and_answer (f23a2ca). 195/198 PASS holds."
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

Eval cases #24 + #25 ("Art.32 status" / "is Art.5 a non-conformity?")
were known-stale from 2026-05-30 through 2026-06-14. Both asserted
the answer must mention an A.5.x bridge — the LLM was stochastic
about citing them, particularly after batch 29a (2026-06-02)
promoted Art.32 + Art.5 to DerivedSpecs with their own direct
evidence. When the article has its own NC verdict, the LLM tends
to answer from that and skip the ISO bridges.

## Resolution — two-part fix on 2026-06-14

**Part 1: shape="cross_framework" validator (b293e8d).**
Replaced literal `must_contain=["A.5"]` with a shape validator
that checks any ISO-bridge-shaped ref appears (A.x.y or ISMS clause
form). Self-match filter strips GDPR sub-paragraphs (Art.32.1.d →
32.1 filtered). The validator catches the architectural failure
mode cleanly: "no ISO bridge ref found" instead of "MISSING
required phrase 'A.5'".

**Part 2: deterministic bridge footer (f23a2ca).**
`rank_and_answer` in `rag/llm_answer.py` now appends
`↳ Bridges to ISO 27001 for Art.X: A.5.1 [NC], A.5.18 [OFI], ...`
when the query is CROSS_FRAMEWORK and Art.* refs are in scope.
Bridges come from `xfw_nodes_list` + `xfw_rel_map` + `posture_by_ref`
already in scope — no extra Neo4j call. Family expansion: a bridge
to Art.32.1.d also surfaces under an Art.32 query (linked ref
check uses `lr.startswith(article + ".")`).

The footer is suppressed if the LLM already cited every bridge —
keeps the surface clean when the LLM does its job, deterministic
when the LLM drops them.

## Why this is the right shape

Cross-framework bridge enumeration is structural information, not
LLM judgement. The LLM's prose remains the primary answer (verdict +
context). The footer is a guaranteed structural enumeration. This is
the same pattern used elsewhere — deterministic data line, LLM prose
around it. The pattern fits cleanly when the underlying data is
authoritative graph traversal (here: IMPLEMENTS/SUPPORTS edges in
Neo4j).

## Eval state
- 2026-06-13 pre-fix: #24 ~30-50% / #25 ~0% pass rate
- 2026-06-14 post-fix: #24 + #25 both consistent PASS (195/198 total)

## Related
- [[posture-discipline-dup-label-fix]] — sibling deterministic-suffix
  pattern (`Evidence:` relabel for Comply)
- [[polish-short-circuit-data-loss-guard]] — sibling LLM-can-drop-
  structural-data class of bugs
- [[curation-phase-b-batch-29a-2026-06-02]] — where Art.32 + Art.5
  got DerivedSpec direct evidence (when the LLM started having
  enough info to drop bridges)
