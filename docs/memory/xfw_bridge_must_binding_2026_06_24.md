---
name: xfw-bridge-must-binding-2026-06-24
description: "SHIPPED 2026-06-24: xfw_proposer now binds each cross-framework bridge to a canonical MUST on the target control via Neo4j leaf/item lookup. Backfilled 58 of 72 existing bridges on Arion (14 uncoverable target Art.5 family + Art.85 with no curated direct_evidence). Bridges are now engine-eligible post tenant approval. Binding heuristic: canonical leaf (register/procedure/record/agreement/programme/policy substring) + owner-shaped MUST item."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

After the unbound drop (b4bf331) cleaned all `extracted` source
unbound findings, 72 xfw_bridge findings remained unbound — but
this is *by-design* unbound, not noise. xfw_proposer creates
cross-framework bridge proposals when an ISO doc evidences a
control with an IMPLEMENTS edge to a GDPR target (or vice versa).
These are pending HITL proposals; user reviews via chat
("what cross-framework findings are pending?").

Problem: even after tenant approval, the bridges had no
`checklist_item_id`, so the engine ignored them (Phase-1
retirement requires bound findings). They were inert.

Fix: bind each bridge to a canonical MUST on the target control.
Once tenant approves, engine sees `1/N` partial credit on the
target leaf.

## Binding heuristic

For each control_ref:

1. **Roll up sub-clauses** to parent article: Art.32.1.b → Art.32;
   Art.5.1.f → Art.5. (ISO refs pass through unchanged.) Curation
   typically happens at the article level; sub-clauses inherit.

2. **Canonical leaf**: prefer one whose id contains
   `register|procedure|record|agreement|programme|policy` — these
   are the "implementation" leaves vs scope-notes or review records.
   Fallback: first leaf alphabetically.

3. **Canonical item**: prefer one matching `owner|charter|
   scope_processing` — the universal "owner" MUST is on most
   register/procedure leaves. Fallback: first item alphabetically.

Cached in `_CANONICAL_BINDINGS_CACHE` per-process — Neo4j queried
once per `propose_for_findings` or `propose_backfill` run.

## Coverage

On Arion's 72 existing xfw_bridge findings:

| Outcome | Count | Examples |
|---|---|---|
| **Bound** | 58 | Art.32 → item:Art.32:reg_owner; Art.28 → item:Art.28:assistance; Art.15 → item:Art.15:proc_exceptions |
| **Unbindable** | 14 | Art.5 family (no curated direct_evidence) + Art.85 |

The 14 unbindable target controls correspond to a curation gap —
Art.5 has 9 DerivedSpecs (Art.5, Art.5.1, Art.5.1.a-f, Art.5.2)
all with empty `direct_evidence`. Curation of Art.5 leaf level
would close the gap (future workstream).

## Code change in `xfw_proposer.py`

Added:
- `_load_canonical_bindings(driver)` — module-cached Neo4j lookup
- `_rollup_sub_clause(ref)` — Art.X.Y.Z → Art.X for GDPR refs
- `_pick_canonical_item(control_ref, bindings)` — chooses the
  item, returns None when uncovered

Threaded `checklist_item_id` param through `_insert_proposal` and
both call sites (`propose_for_findings` + `propose_backfill`).
Bindings cache loaded once per run.

## Semantic caveat

Static MUST binding is approximate. The bridge says "ISO evidence
on source-control X also evidences target-control Y" — but it
doesn't pinpoint *which MUST* on the target. Picking a canonical
`:owner` MUST gives 1/N partial credit, which is reasonable as a
default but may overcount in edge cases.

Tenant always has the chance to reject during Stage-1 review
(bridges land as `review_status='pending'`). The binding only
takes effect on engine posture once approved.

**Future improvement**: replace static binding with per-bridge
LLM evaluation — call the LLM with the bridge excerpt + target
control's MUSTs, ask which MUSTs are actually satisfied. ~$0.01
per bridge, more accurate.

## Why not just drop them like the extracted unbound?

The user explicitly chose "Bind to per-MUST (deeper fix)" from
4 options. The xfw_proposer is a HITL pipeline by design — the
bridges represent real cross-framework relationships from Neo4j
IMPLEMENTS edges. Dropping them would lose cross-framework
signal that's available nowhere else (the IMPLEMENTS edges are
curated knowledge).

## Related

- [[extractor-unbound-drop-2026-06-24]] — sibling fix; drops
  `extracted` source unbound findings entirely. Different design
  pressure: extractor unbound = LLM failure; xfw unbound = bridge
  design.
- [[doc-curation-engine-v1]] — Direction C (per-MUST binding)
  pattern that this extends to cross-framework bridges
