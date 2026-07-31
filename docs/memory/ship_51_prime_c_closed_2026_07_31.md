---
name: ship-51-prime-c-closed-2026-07-31
description: "Ship 51'.c candidate CLOSED without fix — the flagged `control_ref` audit on graph_expander.py turned out to be operator error, not a codebase bug. Documents the Neo4j property-name convention so nobody re-opens the same false alarm: RequirementNode uses `ref`, EvidenceRequirement + ChecklistItem use `control_ref`, and graph_expander.py already respects this split."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 51'.c candidate — Neo4j `control_ref` property audit — CLOSED WITHOUT FIX.

## What triggered the audit

During the "engine sweep + cross-framework applying correctly?"
diagnostic on 2026-07-31, I ran an ad-hoc Cypher probe:

```cypher
MATCH (n:RequirementNode {control_ref: '5.2'}) RETURN n
```

Returned zero rows. I concluded "control_ref property missing from
RequirementNode — any code filtering on it will silently return
nothing" and flagged it as Ship 51'.c.

## What I actually found on audit

**Zero bug. My probe used the wrong property name.**

Neo4j property-name convention (intentional split):

| Label | Property carrying the control ref | Populated count |
|---|---|---|
| `RequirementNode` (control heads) | **`ref`** — e.g. `"5.2"`, `"A.5.15"` | 478 / 478 |
| `EvidenceRequirement` (leaves) | **`control_ref`** | 844 / 844 |
| `ChecklistItem` (MUSTs/SHOULDs) | **`control_ref`** | populated |
| `FulfilmentSpec` | identified by `id` only, no ref field | — |

`graph_expander.py` uses `n.ref` in every Cypher filter that targets
`RequirementNode` (lines 355, 923, 1002, 1008, 1027, 1036, 1105,
1111, 1117 as of `941f45d`). That's the correct property.

All other `control_ref` uses in Cypher across the codebase target
`EvidenceRequirement` or `ChecklistItem` — labels that actually
have the property. Verified via
`grep -rn "n\.control_ref"` across `rag/`, `enrichment/`,
`scripts/`, `api_server.py` — one hit in
`scripts/gen_leaf_scan_catalog.py:434` on `EvidenceRequirement`
(correct).

## What we did

Not a code fix — a comment fix. Added a docstring block near the
top of `rag/graph_expander.py` documenting the property-name
convention, referencing this memory file, so future auditors who
notice `n.ref` don't chase the same ghost.

## Why the naming is asymmetric

Speculation: `RequirementNode` was the earliest RAG-side abstraction
and settled on `ref` before the wider curator tooling standardised
on `control_ref`. Leaves + MUSTs were added later with the fuller
name. Renaming the RequirementNode property would require a Neo4j
migration + touching every Cypher literal in the codebase for zero
functional benefit — the current convention works.

If it EVER needs unification, the migration path is: add `control_ref`
alongside `ref` on RequirementNode (write both, read `ref`),
update code to prefer `control_ref` when present, drop `ref` in a
later cleanup. But there's no operational pain today, so this
candidate stays closed.

## Codified lesson

**Verify Cypher property names against `keys(n)` before flagging a
data-missing bug.** A silent-zero Cypher result on a `{prop: value}`
filter is ambiguous — could be "no rows match" or "no such property
exists." Always follow up with:

```cypher
MATCH (n:LabelName) RETURN keys(n) LIMIT 1
```

before concluding.

## Related

- Ship 51'.a — `document_inventory` templates_block gating fix
- Ship 51'.b — engine kick from intake pipeline (Stage 4.7)
- `rag/graph_expander.py` — carries the docstring pointing back here
