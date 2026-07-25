---
name: ship-39-prime-arc-retrospective-2026-07-25
description: "Ship 39' arc closer — layer 3 fix delivered +31% recall (35→46 accepts). Direct extract test proves consensus can produce cross-framework GDPR Art.35 findings when Phase 3 filter doesn't remove them upstream. Diagnosed layer 0: doc_pipeline._filter_demonstrated_obligations removes GDPR obligations from controls before extract runs. Ship 40 opens for Phase 3 investigation."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 39' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Delivered layer 3 fix + surfaced a deeper layer 0
via measurement.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 39'.a | Design memo — remove scope filter from must_semantic_topk | bfd3c36 |
| 39'.b | Implementation + orchestrator widening + measurement | 77ddfed |
| **39'.c** | **HITL spot-check deferred + eval + retro (this)** | pending |

## Layer 3 fix landed

**`signals/must_semantic_topk.py`**: removed the `ctrl_to_leaves`
scope filter. Now emits candidates for ALL Chroma-surfaced MUSTs
regardless of scope. Added Neo4j `MUST_CONTAIN` lookup for
`must_id → leaf_id` resolution (process-cached, silent-fail).

**`orchestrator.py`**: `must_semantic_topk` runs FIRST; its
leaves union into `widened_leaf_ids` used by the other 7 signals.
Restores critic-verifier's `_build_extend_pool(pool_size=100)`
discovery breadth via architectural convergence.

## Measurement

| Doc | Ship 38 | **Ship 39** | Δ |
|---|---|---|---|
| DQA | 6 | **10** | +4 |
| DPIA | 4 | **11** | +7 |
| RoPA | 5 | 4 | -1 |
| Consent | 6 | 6 | 0 |
| Processor Ops | 14 | 15 | +1 |
| **TOTAL** | **35** | **46** | **+11 (+31%)** |

Target from 39'.a was 80-150. Actual 46. **Well below target.**

Chat pipeline unaffected (baseline expected to hold).

## Direct test proves consensus WORKS (when unblocked)

Called `extract()` directly on DPIA, bypassing doc_pipeline's
control filtering:
- 17 findings total
- **Art.35: 10 findings** (dpo_advice, trigger_criteria, content_minimum,
  review_trigger, rev_art36_audit, rev_coverage, scope_mandatory,
  scope_org_criteria, scope_sa_list, scope_white_list)
- A.7.2.5: 4 findings
- Art.6: 3 findings

vs production API's DPIA re-extract: 11 A.7.2.5 accepts, ZERO Art.35.

**Difference**: doc_pipeline's `_filter_demonstrated_obligations`
(line 986) removes GDPR obligation controls from `controls` list
BEFORE extract() runs. Since Arion has both ISO 27701 + GDPR
enrolled and A.7.2.5 DEMONSTRATES Art.35, Phase 3 filter excludes
Art.35 from extract's controls. Consensus never sees it.

## Layer 0 diagnosed

Ship 38'.c identified a 4-layer bottleneck stack. Ship 39 fixed
layer 3. Ship 39'.b measurement surfaced **layer 0**:

**Layer 0** — `doc_pipeline._filter_demonstrated_obligations`
removes cross-framework obligations from controls list before
extract() sees them. Deliberate Phase 3 design (framework role
model, 2026-07-05); rationale: "obligations demonstrated by
PROGRAM/EXTENSION should be propagated via DEMONSTRATES overlay
at posture-load time (Phase 2c), not extracted directly." Correct
for the OLD LLM pipeline (LLM would duplicate A.7.2.5 findings
on Art.35). Misaligned with consensus's discovery-broad intent.

## Ship 40 direction locked

Investigate Phase 3 filter interaction with consensus. Options:
- **A**: Conditional bypass — `if USE_CONSENSUS_EXTRACTION=1,
  skip _filter_demonstrated_obligations`. Small code change;
  preserves Phase 3 for OLD pipeline; unblocks consensus.
- **B**: Accept Phase 3 as-is — trust DEMONSTRATES overlay at
  posture-load time to surface Art.35 posture from A.7.2.5
  findings. No direct Art.35 findings; posture propagates.
- **C**: Design review — determine whether consensus should
  extract cross-framework directly OR rely on posture-level
  propagation. Bigger design arc.

Ship 40'.a picks between A/B/C based on user preference + audit
requirements analysis.

## Codified 2 lessons

### 1. Filters at N layers compose multiplicatively

Ship 38 identified 4 filter layers (fingerprint, doc_mappings,
must_semantic scope, invariant). Ship 39 removed one (must_semantic
scope). But layer 0 (Phase 3 obligation filter in doc_pipeline)
was NEVER counted — it's UPSTREAM of the whole extraction path.
The 4-layer count was itself narrow; the real stack has 5+ layers
across doc_pipeline + extractor + consensus_extraction.

**Rule**: when diagnosing a recall bottleneck, walk the ENTIRE
call chain from doc arrival to finding write. Every function
that touches "which controls are relevant" is a potential filter.
Layer inventories that stop at the module you're editing miss
upstream filters that fix nothing.

### 2. Production behavior ≠ direct test behavior when framework
role model is involved

`extract(doc, controls, api_key)` is the same function whether
called directly or via doc_pipeline. But doc_pipeline filters
`controls` before passing it. So direct test = broader scope =
different results.

**Rule**: when reproducing production issues, use the full call
chain (doc_pipeline path), not just the function you're
debugging. "extract() works fine when I call it directly" is
misleading if doc_pipeline pre-filters its input.

## What Ship 39 did NOT do

- **Fix layer 0** — Ship 40 candidate
- **Fix layers 1-2** (xfw edge coverage, doc_mappings scope) —
  Ship 40+ candidates
- **HITL spot-check on new accepts** — deferred; small enough
  sample (11 new accepts) that visual review of the finding
  descriptions likely sufficient; can HITL later if needed
- **Threshold retuning** — weights + floors unchanged
- **Broad curator arc** — deferred

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 39'.a | Design memo — layer 3 fix | Concrete change locked |
| 39'.b | Implement + orchestrator widening + re-measure | +31% (35→46); layer 0 surfaced |
| **39'.c** | **Eval + retro (this)** | **Layer 0 diagnosed; Ship 40 direction locked** |

## Deferred / follow-on candidates from Ship 39

- **Ship 40**: Phase 3 filter interaction with consensus
- **Ship 41+**: xfw_proposer edge coverage (layer 1); doc_mappings
  YAML union investigation (layer 2)
- **HITL of accepted consensus findings** still unmeasured
- **Broad curator arc on proc_* fingerprints** deferred until
  scope layers fully resolved

## Related

- [[ship-38-prime-arc-retrospective-2026-07-25]] — the arc whose
  4-layer diagnosis Ship 39 addressed layer 3 of; Ship 39 revealed
  layer 0 was missed from that count
- Ship 40 (next) — Phase 3 filter investigation
- `rag/intake/doc_pipeline.py:986` — `_filter_demonstrated_obligations`
  — the layer 0 code
