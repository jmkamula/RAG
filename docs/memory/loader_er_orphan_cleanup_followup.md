---
name: loader-er-orphan-cleanup-followup
description: Loader prunes orphan ChecklistItems but not orphan EvidenceRequirement nodes. Manifests as engine 0/(N+M) instead of 0/N when controls have leaf ids renamed during promotion. Manual cleanup needed; loader fix pending.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e616419f-f804-435c-89a9-52c1d411073d
---

`enrichment/documents/load_to_neo4j.py` has two orphan-pruning passes:

1. `_prune_leaf_orphans` — drops MUST/SHOULD edges to ChecklistItems
   that aren't in the current leaf's spec.
2. `_delete_orphan_items` — drops ChecklistItem nodes with no incoming
   MUST/SHOULD edges from ANY EvidenceRequirement.

Missing: orphan EvidenceRequirement pruning. If a leaf's `id` field
changes (e.g. promoting a single-leaf `req:A.8.24:encryption_policy`
to a 4-leaf set with `req:A.8.24:cryptography_policy` as the policy
leaf), the old EvidenceRequirement node stays in Neo4j with its
REQUIRES_EVIDENCE edge to the control intact.

**Why:** Loader was designed leaf-conservative — only act on leaves
currently in the spec. Made sense when leaves were stable IDs and
shape (only items churned). Phase B promotions break that assumption
because spine variants need different leaf-type names
(`encryption_policy` → `cryptography_policy` + `key_register` +
`applicable_crypto_scope` + `crypto_program_review`).

**How to apply:**

*Short-term (manual cleanup, applied in batch 23 commit pending):*
After running `load_to_neo4j.py` on any batch with id-rename
promotions, run a one-shot Cypher cleanup:

```python
import enrichment.documents.document_requirements as m
valid_ids = {r.id for r in m.ALL_EVIDENCE_REQUIREMENTS}
# Find orphan EvidenceRequirements where id not in valid_ids
# DETACH DELETE them
# Also re-run _delete_orphan_items semantics:
# MATCH (i:ChecklistItem) WHERE NOT EXISTS { MATCH (:EvidenceRequirement)-[:MUST_CONTAIN|SHOULD_CONTAIN]->(i) } DETACH DELETE i
```

*Long-term (loader fix, not yet done):* Add `_delete_orphan_ers`
function to `load_to_neo4j.py` that runs after all leaves are
processed. Compare Neo4j EvidenceRequirement ids against the
loader's pass set. DETACH DELETE any orphans. Then re-run the
existing `_delete_orphan_items` to clean up newly-orphaned items.

Surfaces as: engine reports "0/(N+M) children satisfied" instead of
"0/N" — N is the real count, M is the orphan count. Tested in batch
23 — A.8.24 reported "0/5 children satisfied" because the old
`encryption_policy` EvidenceRequirement still linked. After cleanup
returns to "0/4".

GDPR orphans noticed during batch 23 cleanup (req:Art.16/17/25/32/6
various) suggest this gap has existed since earlier curation passes.
Not in batch 23 scope to clean — left for separate followup.

Related: [[loader-orphan-cleanup-followup]] (the item-orphan cleanup
this builds on).
