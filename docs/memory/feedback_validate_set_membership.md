---
name: feedback-validate-set-membership
description: "RULE: when computing a set difference between two systems (e.g. 'which items in A are stale because not in B'), prove both sets are computed the same way the production code computes them — not via a hand-rolled scan. Surfaced 2026-06-27 by the queue sweep: 96 valid findings were soft-deleted as 'stale' because my catalog-membership scan used dir() + isinstance(EvidenceRequirement) and missed leaves nested in DerivedSpec.direct_evidence. The loader uses ALL_EVIDENCE_REQUIREMENTS + ALL_DERIVED_SPECS.direct_evidence as its valid_ev_ids — that's the canonical union."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## Rule

When acting on a "set difference" between system A (truth) and
system B (state to clean), **prove both sets are computed the same
way the production code computes them**. Hand-rolled scans across
the canonical sources are the bite.

For ratio metrics, the analog is "validate the denominator"
([[feedback-validate-the-denominator]]). For set-difference
decisions (delete-what-shouldn't-be-there), the bite is the
*membership predicate* — the rule for what counts as "in A".

## How it bit (2026-06-27 queue sweep)

I quantified Stage-1 queue staleness by:

1. Building `catalog_items` via `dir(drm)` + `isinstance(EvidenceRequirement)` —
   picks up only module-level `EvidenceRequirement` instances.
2. Classifying any `checklist_item_id` not in that set as "stale".
3. Soft-deleting 96 such findings.

The bug: `EvidenceRequirement` instances also live nested inside
`DerivedSpec.direct_evidence` (GDPR derived-from chains, where a
single article-level RequirementNode is satisfied by multiple
sub-article leaves — e.g. `req:Art.16:rectification_procedure` is
`DerivedSpec.direct_evidence` of `spec:GDPR:2016/679:Art.16`, NOT
exported as a module-level `REQ_...` variable).

My scan missed them. 96 valid catalog items looked "stale" because
their parent ER wasn't visible to my scan.

## The canonical union (matches the production loader)

```python
from enrichment.documents.document_requirements import (
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)

all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
    er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
]
valid_must_ids = {
    ci.id
    for er in all_ers
    for ci in list(er.must_contain) + list(er.should_contain)
}
```

This is exactly what `enrichment/documents/load_to_neo4j.py` uses for
`valid_ev_ids` (line ~471). Reuse it; don't reinvent.

## How to apply

Before treating any `not in catalog` finding as a delete candidate:

1. **Check the production loader's predicate**. If the loader has
   a `valid_ev_ids` or similar, use that exact construction.
2. **Spot-check 2-3 'stale' items against the catalog file itself**.
   If you can grep `git grep 'item:Art.16:correction_record'` and
   find a real definition, your scan was wrong.
3. **Diff counts before acting**. Production catalog count vs your
   computed catalog count. Mismatch = bug in the membership predicate.

In the 2026-06-27 case:
- Python catalog ChecklistItems: **4278** (proper union)
- Neo4j ChecklistItems: **4278**
- My hand-rolled scan: **4133** (missed 145 DerivedSpec children)

The mismatch (4133 vs 4278) was the smoking gun. Had I noticed it,
I'd have caught the bug before soft-deleting 96 findings.

## Sister lessons

- [[feedback-validate-the-denominator]] — same pattern for ratios:
  validate the denominator universe before treating the ratio as
  ground truth. Today's lesson is the *categorical* version (set
  membership) of yesterday's *cardinal* version (ratio).
- [[feedback-telemetry-before-trouble]] — instrument absence, not
  just rejection. If the sweep had reported `python_catalog_count vs
  neo4j_count` before acting, the mismatch would have flagged.

## Related

- [[stage1-queue-sweep-2026-06-27]] (planned next entry) — the
  arc where this surfaced and was repaired.
