---
name: loader-er-orphan-cleanup-followup
description: RESOLVED 2026-06-01. Loader now prunes orphan EvidenceRequirement nodes (id-rename promotions). Valid-id set includes both ALL_EVIDENCE_REQUIREMENTS and each DerivedSpec.direct_evidence.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e616419f-f804-435c-89a9-52c1d411073d
---

`enrichment/documents/load_to_neo4j.py` has three orphan-pruning passes:

1. `_prune_leaf_orphans` — drops MUST/SHOULD edges to ChecklistItems
   that aren't in the current leaf's spec.
2. `_delete_orphan_ers` (added 2026-06-01) — drops EvidenceRequirement
   nodes whose id is not in the loader's valid set.
3. `_delete_orphan_items` — drops ChecklistItem nodes with no incoming
   MUST/SHOULD edges from ANY EvidenceRequirement.

Order matters: ER pruning must run BEFORE item pruning, because
deleting an orphan ER creates new orphan items that the item pass
then sweeps up.

**Why the original design was leaf-conservative:** loader was built
when leaves were stable IDs and shape (only items churned across
versions). Phase B promotions broke that assumption — spine variants
need different leaf-type names (`encryption_policy` →
`cryptography_policy` + `key_register` + `applicable_crypto_scope` +
`crypto_program_review`). Without ER pruning, the old node stayed
attached and the engine reported "0/(N+M) children satisfied" instead
of "0/N".

**How to apply:** The valid-id set for the orphan check must include
**both** sources the loader writes to Neo4j:

```python
valid_ev_ids = {r.id for r in ALL_EVIDENCE_REQUIREMENTS} \
             | {req.id for ds in ALL_DERIVED_SPECS for req in ds.direct_evidence}
```

The second clause is critical. DerivedSpec direct_evidence ids
(req:Art.16/17/25/32/6/etc.) are nested in the DerivedSpec definitions,
not in the registry list — but the loader still MERGEs them to Neo4j.
A naive check against ALL_EVIDENCE_REQUIREMENTS only will incorrectly
flag them as orphans and delete legitimate data.

**Surfaces as:** engine reports "0/(N+M) children satisfied" instead of
"0/N" — N is the real count, M is the orphan count. Was the reason
A.8.24/A.8.34 reported "0/5 children satisfied" in batch 23 before the
manual Cypher cleanup ran. With the loader fix, this surface bug
cannot recur.

Related: [[loader-orphan-cleanup-followup]] (the item-orphan cleanup
this builds on).
