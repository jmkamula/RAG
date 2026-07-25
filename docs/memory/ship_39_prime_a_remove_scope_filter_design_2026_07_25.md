---
name: ship-39-prime-a-remove-scope-filter-design-2026-07-25
description: "Ship 39'.a — design memo for the layer 3 fix. Remove the scope filter from `must_semantic_topk` signal so Chroma-surfaced MUSTs from cross-framework mirrors (Art.35 for DPIA) become candidates instead of being dropped pre-aggregator. Restores critic-verifier's `_build_extend_pool(pool_size=100)` discovery breadth. Expected to recover most of the Ship 32 Path A recall on procedural docs while preserving Ship 33 precision."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 39'.a — opens Ship 39 arc. Ship 38'.c diagnosed a 4-layer
bottleneck stack; this arc addresses layer 3 (scope filter on
`must_semantic_topk`) per user direction.

## The concrete fix

`rag/intake/consensus_extraction/signals/must_semantic_topk.py`
currently filters Chroma results to leaves in scope:

```python
# Current — over-restrictive:
for must_id in must_ids:
    parts = (must_id or "").split(":")
    if len(parts) < 3: continue
    ctrl = parts[1]
    for leaf_id in ctrl_to_leaves.get(ctrl, []):   # ← the filter
        candidates[(leaf_id, must_id)] = cfg.must_semantic_weight
```

`ctrl_to_leaves` maps `control_ref → leaf_ids` for leaves in
`scoped_leaf_ids`. If Chroma surfaces an Art.35 MUST but Art.35
isn't in `scoped_leaf_ids`' controls, the MUST is dropped.

**Ship 39 change**: emit candidates for ALL Chroma-surfaced MUSTs
regardless of scope. The aggregator still needs corroboration
(min_corroborators + accept_floor) to auto-accept, so scope-only
candidates (fired by only `must_semantic_topk`) can't reach
accept alone.

```python
# Ship 39 target:
for must_id in must_ids:
    parts = (must_id or "").split(":")
    if len(parts) < 3: continue
    ctrl = parts[1]
    # Look up the leaf_id via Neo4j (find the primary leaf under
    # this control that owns this MUST). If no leaf is found (edge
    # case), skip.
    for leaf_id in _lookup_leaf_for_must(must_id, ctrl):
        candidates[(leaf_id, must_id)] = cfg.must_semantic_weight
```

Detail: since `must_semantic_topk` currently uses `scoped_leaf_ids`
to know which leaf a must_id belongs to, removing the filter means
we need a different way to resolve `must_id → leaf_id`. Options:

1. **Query Neo4j for `(EvidenceRequirement)-[:MUST_CONTAIN]->(ChecklistItem)`
   where item.id = must_id** — returns the parent leaf. One query
   per unbound MUST; batchable.
2. **Load the leaf-scan catalog + reverse-index must_id → leaf_id
   in a cache** — precomputed lookup.
3. **Use standard/control from must_id parse + look up leaf by
   convention** — brittle if leaf ids don't follow a strict pattern.

Option 2 is fastest at runtime (lazy-cached dict); option 1 is
simpler code. Ship 39'.b picks based on measurement of query volume.

## Expected impact

**On DPIA specifically**: Chroma with the DPIA doc's text at
top-K=30 should surface Art.35 MUSTs (trigger_criteria, dpo_advice,
etc.) alongside A.7.2.5. Currently ~10 A.7.2.5 MUSTs in candidates_sample;
post-fix should also include Art.35 MUSTs.

For Art.35:trigger_criteria + dpo_advice on DPIA (Ship 38'.b direct
test confirmed these fingerprint-match):
- Now become candidates via `must_semantic_topk` (0.30 weight)
- Plus `fingerprint_keyword` (0.50) if the fingerprint matches
- Plus `semantic_fit_gate` (±0.30) since fingerprint provides
  excerpt
- Plus `per_protocol_scope` (0.10) if control is in per-standard
  Chroma
- Total score potentially ≥ 1.10 with corrob ≥ 3 → accept

**On 5-doc corpus totals**:
- Ship 32 Path A: 272
- Ship 38 current: 35
- Ship 39 target: ~80-150 (middle path — recovers cross-framework
  discovery without hitting old pipeline's noise level)

Failure signals:
- Ship 39 > 200 accepts — over-permissive (`must_semantic_topk`
  alone fires too broadly)
- Ship 39 < 50 accepts — fix didn't help (need deeper investigation)
- HITL spot-check on new accepts shows > 30% false-positive rate

## What Ship 39 does NOT do

- **Fix layers 1-2** (xfw edge coverage + doc_mappings scope) —
  Ship 40+ if Ship 39 alone isn't sufficient
- **Add new signals** — using existing signal set
- **Retune thresholds** — weights + floors unchanged from Ship 38
- **Broad curator arc** — only layer 4; deferred

## Chat pipeline unaffected

Extraction consensus is a separate subsystem from Ship 1 chat
consensus. Chat classifier's signals + aggregator + gatekeeper
untouched. Eval baseline expected to hold.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **39'.a** (this) | Design memo | Concrete fix + expected numbers + failure signals locked |
| 39'.b | Implement + re-measure | 5-doc corpus numbers; DPIA Art.35 landing check |
| 39'.c | HITL spot-check + eval + retro | Precision on new accepts; retro codifies whether recall recovery is production-appropriate |

## Related

- [[ship-38-prime-arc-retrospective-2026-07-25]] — the arc whose
  layer-stack diagnosis locked this fix
- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  arc where the mis-applied filter was introduced
- Critic-verifier `_build_extend_pool` — the reference behavior
  this fix restores
