---
name: neo4j-graph-unused-element-warnings
description: "Eval suite spams Neo4j 01N51 ('RELATED_TO' rel type) and 01N52 ('confidence' edge property) warnings — both referenced by graph_expander queries but absent from the graph data"
metadata: 
  node_type: memory
  type: project
  originSessionId: ab2912f3-a587-4819-891f-14d62eba574c
---

The eval suite log is polluted with two Neo4j notifications fired on every relevant graph query — same architectural shape as [[applies-when-warning-suppression]] (queries anticipate data that hasn't been populated):

- **01N51** — `relationship type "RELATED_TO" does not exist`. From `graph_expander.py`'s ancestor/lateral walk: `OPTIONAL MATCH (n)-[:RELATED_TO]-(lateral:RequirementNode)`. No edges in the current graph carry this label.
- **01N52** — `property key "confidence" does not exist`. From the xfw expander reading `r_out.confidence` / `r_in.confidence` on `IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE` relationships. The edges exist and are populated (xfw graph is live), but no edge carries the `confidence` property.

**Why:** Per-query warnings during the eval run obscure real ones, and the warnings themselves don't say whether the missing data is *expected* (Phase-1 placeholder, like applies_when) or *unintended* (data drift / dead query branch). The category needs a decision before suppression is safe.

**How to apply:** Resolve as a single Neo4j-schema audit pass — (a) `RELATED_TO`: was it intended to be populated and never was, or is the OPTIONAL MATCH branch dead and should be removed from `graph_expander.py`? Cheap fix either way: populate one edge to register the type, OR delete the branch. (b) xfw `confidence`: were `IMPLEMENTS`/`SUPPORTS`/`ENABLES`/`GOVERNANCE` edges supposed to carry a confidence score that never got written, or is the read aspirational? Check whether anything downstream consumes the field (today it's always `None`/missing). (c) Once (a) and (b) resolved, suppress remaining noise at driver level via `notifications_disabled_classifications=['UNRECOGNIZED']` — same one-liner planned for [[applies-when-warning-suppression]]. **Do not blanket-suppress before resolving (a)/(b)**, since that would hide legitimate `01N51`/`01N52` warnings for future schema drift.

Related: [[applies-when-warning-suppression]], [[applies-when-er-resolver-gap]], [[applies-when-phase1-regression-tests]].
