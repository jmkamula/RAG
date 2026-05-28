---
name: loader-orphan-cleanup-followup
description: "SHIPPED 2026-05-28: load_to_neo4j.py is now declarative — per-leaf edge prune + final orphan-item sweep. Code is the single source of truth; reloading idempotently restores Neo4j to exact code shape."
metadata: 
  node_type: memory
  type: project
  originSessionId: 868f217c-318d-4e60-8b45-33ccd7d5dd9c
---

**Status:** SHIPPED 2026-05-28. The loader at `enrichment/documents/load_to_neo4j.py` now performs declarative orphan pruning. Reloading takes Neo4j back to exactly what `ALL_EVIDENCE_REQUIREMENTS` (and `DerivedSpec.direct_evidence`) defines — no leftover state from prior loads.

**Original problem:** the loader used Cypher `MERGE` exclusively and never deleted, so any ChecklistItem or MUST_CONTAIN/SHOULD_CONTAIN edge from a previous load survived forever, even after the current Python definition stopped referencing it. The leaf evaluator's `MATCH (er)-[:MUST_CONTAIN]->(item)` then returned the code-defined items PLUS stale ones, inflating per-leaf MUST count and producing false NC verdicts. Multi-leaf curation under [[curation-program-full-multi-leaf]] re-uses leaf ids across redesigns, rewrites checklist item lists, and shifts items between MUST and SHOULD — every such change created orphans.

**Implementation:**

Two helpers in `load_to_neo4j.py`:

- `_prune_leaf_orphans(session, req, dry_run)` — runs after MERGEing all code-defined items for a leaf. Drops MUST_CONTAIN edges to items not in `req.must_contain`, then SHOULD_CONTAIN edges to items not in `req.should_contain`. Scoped to one leaf, so items legitimately moving between leaves keep their new-leaf edge.
- `_delete_orphan_items(session, dry_run)` — single pass at the end of the load. Removes ChecklistItem nodes with no remaining MUST_CONTAIN or SHOULD_CONTAIN edges from any EvidenceRequirement. `DETACH DELETE` removes incidental edges (e.g. DERIVED_FROM back to RequirementNode).

Both call paths run in dry-run too (counts only, no writes). Both EvidenceRequirement and `DerivedSpec.direct_evidence` leaves are pruned. The summary block surfaces edges + items pruned per run; `0 (clean state)` on a no-op run.

**How to apply:** running `python3 enrichment/documents/load_to_neo4j.py` is now sufficient — no manual orphan audit needed after multi-leaf promotion.

**Verified end-to-end 2026-05-28** on the live Neo4j:

| Scenario | Expected | Result |
|---|---|---|
| Load on clean state | 0 prunes | "Pruned stale edges: 0 (clean state)" |
| 3 synthetic orphan edges on register | 3 edges + 3 items dropped | "Pruned: 2M + 1S edges, 3 orphan items" |
| Item attached to wrong second leaf | stray edge dropped, item survives | item ends with exactly 1 leaf (the legitimate one) |
| Full-corpus drift audit post-load | 0 drift across 146 leaves | 0 |

**Caveat:** dry-run mode under-counts orphan items because the per-leaf prune deletes aren't simulated, so items that *would* become orphan still appear attached during the orphan-item sweep. Reported count of edges-to-be-pruned is accurate; reported orphan-items count in dry-run can read 0 even when real run would delete many. Not blocking — real-run output is the source of truth.

**Linked work:** [[curation-program-full-multi-leaf]] (the source of this hygiene burden); [[curation-session-state-2026-05-26]] (the manual cleanup session this fix obsoletes).
