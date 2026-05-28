---
name: loader-orphan-cleanup-followup
description: "Decided 2026-05-28 to extend load_to_neo4j.py with declarative orphan pruning (option b). Until shipped, prune orphans manually as encountered during multi-leaf promotion."
metadata: 
  node_type: memory
  type: project
  originSessionId: 868f217c-318d-4e60-8b45-33ccd7d5dd9c
---

`enrichment/documents/load_to_neo4j.py` uses Cypher `MERGE` exclusively and never deletes — so any ChecklistItem or MUST_CONTAIN/SHOULD_CONTAIN edge that existed at the previous load survives forever, even if the current Python definition no longer references it. This breaks the leaf evaluator: `MATCH (er)-[:MUST_CONTAIN]->(item)` returns the code-defined items PLUS stale ones, inflating the per-leaf MUST count and producing false NC verdicts.

**Why:** Multi-leaf curation (per [[curation-program-full-multi-leaf]]) re-uses leaf ids across redesigns, rewrites checklist item lists, and shifts items between MUST and SHOULD. Every such change creates orphans under MERGE-only semantics. Session 2026-05-28 found 19 orphans across 4 calibrated controls (A.5.18 procedure: 7, A.5.2 matrix: 1, A.8.2 procedure: 9, Art.30 register: 1, Art.15 dsar_response: 1 dual-edge).

**Decision (option b):** extend `load_to_neo4j.py` so after MERGEing the code-defined items for each leaf, it executes:

```cypher
MATCH (er:EvidenceRequirement {id: $leaf_id})-[rel:MUST_CONTAIN|SHOULD_CONTAIN]->(i:ChecklistItem)
WHERE NOT i.id IN $code_item_ids
DELETE rel
// then a second pass deletes orphan items that have no remaining references
```

This makes the loader fully declarative — the Neo4j shape after a load equals exactly what `ALL_EVIDENCE_REQUIREMENTS` says, no leftover state. Rejected (a) post-load sweep utility because the two-step process is easy to forget.

**How to apply (until shipped):** at every multi-leaf promotion, after running the loader, audit the touched leaves with this snippet (the one used in session 2026-05-28):

```python
code = {r.id: ({c.id for c in r.must_contain}, {c.id for c in r.should_contain})
        for r in ALL_EVIDENCE_REQUIREMENTS if r.control_ref in TARGETS}
# query Neo4j for MUST/SHOULD edges per leaf; diff against code; DETACH DELETE orphans
```

The ad-hoc audit + DETACH DELETE pattern from session 2026-05-28 (calibrations #2-#5 cleanup) is the manual fallback.

**Risks of the integrated fix:**
- A buggy edit could nuke live edges. The loader change must include a unit test pinning "load → no-op load produces zero edge changes" and "load with item removed from code drops exactly that edge".
- Items that move BETWEEN leaves (rare but possible) must be detected before deletion — the orphan check is per-leaf, so an item moving from leaf A to leaf B would correctly drop the A edge while keeping the B edge.

**Linked work:** [[curation-program-full-multi-leaf]] (the source of this hygiene burden); [[curation-session-state-2026-05-26]] (where A.5.2 orphan was first noted as "1 orphan item:A.5.2:approval").
