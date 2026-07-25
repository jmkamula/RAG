---
name: ship-38-prime-arc-retrospective-2026-07-25
description: "Ship 38' arc closer — two-pronged remedy diagnosed a deeper bottleneck. Invariant relaxation + 5 curator fingerprint fixes delivered +2 accepts on 5-doc corpus (33→35). Real finding: the scope narrowing at doc_mappings target_leaves + the scope-filter I put on must_semantic_topk block the LLM-discovery breadth critic-verifier had via `_build_extend_pool(pool_size=100)`. Ship 39 restores that breadth by removing the scope filter."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 38' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Delivered the two-pronged remedy Ship 37 diagnosed +
surfaced a deeper architectural bottleneck via measurement.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 38'.a | Design memo — relaxation + curator scope + measurement plan | ad0e143 |
| 38'.b | Invariant escape clause + 5 curator fingerprint fixes + re-measure | e36ef1c |
| **38'.c** | **Retrospective + Ship 39 direction locked (this)** | pending |

## What worked (partial)

**Invariant relaxation code shipped**: `no_excerpt_escape_score=1.5`
+ `no_excerpt_escape_corrob=3` config knobs. Escape clause in
aggregator: no-excerpt candidates with strong multi-signal
corroboration route to arbiter instead of drop.

**5 curator fingerprint fixes**:
- `req_A_7_4_3_accuracy_procedure.yaml` — 2 MUSTs (inaccuracy
  response + prevention) got verb-driven doc-prose keywords
- `req_Art_35_dpia_procedure.yaml` — 2 MUSTs (trigger_criteria +
  dpo_advice)
- `req_B_8_2_2_purpose_limitation_procedure.yaml` — 1 MUST
  (proc_technical_binding)

All new keyword sets verified present in the target docs' text.

## Re-measurement result

| Doc | Ship 36 accept | Ship 38 accept | Δ |
|---|---|---|---|
| DQA | 4 | **6** | +2 |
| DPIA | 4 | 4 | 0 |
| RoPA | 5 | 5 | 0 |
| Consent | 6 | 6 | 0 |
| Processor Ops | 14 | 14 | 0 |
| **TOTAL** | **33** | **35** | **+2** |

Target from 38'.a was 60-100 accepts. Actual +2 (6% improvement).
**Well below target.**

Arbiter zone: 0 across all docs. **Escape clause never fired** —
no candidates hit score ≥1.5 + corrob ≥3 AND had no-excerpt.

## What DIDN'T work (and why)

**Art.35 curator fix on DPIA doc**: keywords verified present in
doc text; fingerprint matcher fires when tested in isolation with
broader scope. But the production DPIA re-extract's
`candidates_sample` shows ONLY A.7.2.5 MUSTs — no Art.35.

**Root cause**: DPIA's `target_leaves` (populated by
`_scope_controls_via_doc_mappings`) contains A.7.2.5 leaves but
not Art.35 leaves. My consensus's `must_semantic_topk` signal
explicitly filters Chroma results to leaves in `scoped_leaf_ids`
(which comes from `target_leaves` when populated). So Art.35 MUSTs
are dropped before the aggregator sees them, regardless of what
curator fix I make on the Art.35 fingerprint YAML.

## The deeper diagnostic

Ship 32→38 uncovered a 4-layer bottleneck stack (deepest first):

1. **xfw_proposer edge-type coverage** — walks SUPPORTS/ENABLES/
   GOVERNANCE but not IMPLEMENTS/DEMONSTRATES. Verified: DPIA
   produces 4 A.7.2.5 findings + 2 xfw_bridge findings (both to
   ISO 27001 via SUPPORTS). Zero GDPR Art.35 findings despite
   `A.7.2.5 -IMPLEMENTS→ Art.35` edge existing in Neo4j.
2. **doc_mappings `target_leaves` scope narrowing** — populated
   from YAML matches only; when populated, replaces broader scope
   with narrow scope. Art.35's dpia_procedure leaf has its own
   doc_mappings YAML but the multi-YAML union may not consolidate
   as expected.
3. **My scope filter on `must_semantic_topk`** — my signal at
   `signals/must_semantic_topk.py` explicitly filters Chroma
   results to `scoped_leaf_ids`' controls. Critic-verifier's
   `_build_extend_pool(pool_size=100)` had NO such filter. That's
   the recall-loss mechanism.
4. **Fingerprint catalog gap on `proc_*` MUSTs** — Ship 38'.b's
   curator fix addressed 5 of these. Modest impact (+2 accepts on
   DQA) because layer 3 blocks the rest from reaching the fingerprint
   test.

Ship 38 addressed layer 4 (partially). Layers 1-3 are Ship 39+ work.

## What Ship 39 does

**User direction locked**: "Ship 39 = remove scope filter on
must_semantic_topk (Option 1)".

Concrete change in `rag/intake/consensus_extraction/signals/must_semantic_topk.py`:

```python
# Ship 38 code (over-restrictive):
for must_id in must_ids:
    parts = must_id.split(":")
    ctrl = parts[1]
    for leaf_id in ctrl_to_leaves.get(ctrl, []):  # ← filter
        candidates[(leaf_id, must_id)] = cfg.must_semantic_weight

# Ship 39 target (restores critic-verifier breadth):
# Emit candidates for ALL Chroma-surfaced MUSTs regardless of
# whether their leaf's control is in scoped_leaf_ids. Aggregator
# still needs corroboration to accept, so weak-scope candidates
# won't over-accept.
```

Expected impact:
- must_semantic_topk fires on ~30 MUSTs per doc (currently ~5-108
  depending on how many are in scope)
- Candidates from cross-framework mirrors surface (Art.35 for DPIA;
  27701 mirrors for other GDPR docs)
- Aggregator's corroboration + LLM arbiter still gate acceptance —
  scope-only candidates need OTHER signals to corroborate

**Not touched by Ship 39**: layers 1-2 (xfw edge coverage, doc_mappings
scope). Ship 40+ if needed after re-measurement.

## Production exposure clarified

Ship 36'.c said "88% reduction" and "invariant is the constraint."
Ship 38'.c reveals: the constraint is deeper. Consensus in current
form loses ~78% on DPIA (27→6) primarily due to layers 1-3, NOT the
invariant.

For any real customer working GDPR compliance via ISO 27701 mirrors,
this loses substantial coverage. **Default OFF is the right ship
state until Ship 39 fixes layer 3.**

Demo tenant currently has flag=1. Keeping it on for measurement
value; the recall gap is well-understood and won't confuse anyone
who reads the arc retros.

## Codified 2 lessons

### 1. Signal filter discipline doesn't transfer verbatim from chat to extraction

Chat consensus filters signals to the query. Extraction's discovery
role is orthogonal — for a doc, discovery beyond scope is the whole
point of the LLM pass. I applied scope-filter discipline from
chat consensus to extraction where it doesn't belong.

**Rule**: when mirroring an architecture across domains, check
which invariants are domain-specific vs cross-cutting. Filter
discipline is domain-specific: chat filters signals to query
scope; extraction should NOT filter signals to doc scope (defeats
discovery).

### 2. Curator fixes don't help if scope narrowing precedes them

My 5 curator YAML fixes were surgically correct but only 2 landed
because the other 3 affect leaves that aren't in production
target_leaves scope. Fixing keywords for MUSTs whose leaves aren't
even considered is a no-op.

**Rule**: before doing curator work on a specific fingerprint
YAML, verify the target leaf is actually reachable in the
production pipeline's scope. Otherwise the curator work is
wasted.

## What Ship 38 did NOT do

- **Fix layers 1-3** — Ship 39+ work
- **Broad curator arc on all proc_* fingerprints** — no point until
  scope is fixed (per lesson 2)
- **Flip flag off on demo** — leaving on for measurement value +
  team visibility
- **Retire invariant** — the escape clause is in place; unclear if
  it'll matter until scope is fixed

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 38'.a | Design memo | Relaxation + curator scope + measurement plan locked |
| 38'.b | Implement + curator + re-measure | +2 accepts; scope narrowing surfaced as deeper bottleneck |
| **38'.c** | **Retro + Ship 39 direction (this)** | **Layer stack + Ship 39 fix locked** |

## Deferred / follow-on candidates from Ship 38

- **Ship 39**: remove scope filter on `must_semantic_topk` (locked)
- **Ship 40+ candidate 1**: fix xfw_proposer edge-type coverage
  (walk IMPLEMENTS/DEMONSTRATES to GDPR)
- **Ship 40+ candidate 2**: `_scope_controls_via_doc_mappings`
  should union across ALL matching YAMLs (not just the highest-
  scoring one) — investigate why DPIA's Art.35 YAML matches
  aren't consolidating
- **Broad curator arc on proc_* fingerprints** — only worth doing
  AFTER layers 1-3 are fixed
- **HITL of ACCEPTED consensus findings** — still unmeasured;
  precision on the other side of the aggregator remains unknown

## Related

- [[ship-37-prime-arc-retrospective-2026-07-25]] — the HITL that
  motivated this arc's remedy
- [[ship-36-prime-arc-retrospective-2026-07-25]] — the cutover
  arc whose "invariant is the constraint" claim Ship 38 partially
  corrects
- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  arc whose signal filter Ship 39 will fix
