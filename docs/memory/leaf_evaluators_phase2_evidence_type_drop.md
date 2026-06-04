---
name: leaf-evaluators-phase2-evidence-type-drop
description: "SHIPPED 2026-06-04: leaf_evaluators._fetch_recognised_items Phase-2 path no longer filters on cd.evidence_type=leaf.evidence_type. With checklist_item_id populated (now exercised by workbook intake), the doc-level evidence_type filter was over-restrictive — one workbook legitimately feeds many leaves of different evidence_types."
metadata: 
  node_type: memory
  type: project
  originSessionId: b7702385-93e8-4fb5-8bcc-881816acb712
---

SHIPPED 2026-06-04 alongside the workbook intake → Stage 1 merge.

`rag/posture/leaf_evaluators.py::GenericLeafEvaluator._fetch_recognised_items`
has TWO paths:
- **Phase-2 (per-item)**: filter findings by `df.checklist_item_id = ANY(must_item_ids)`.
- **Phase-1 (coarse fallback)**: filter findings by `df.control_ref + cd.evidence_type`.

Both originally JOIN'd `client_documents` and required `cd.evidence_type = leaf.evidence_type`. That predicate was a safety net from the era when nobody populated `checklist_item_id` — without it, the per-item path would match ANY finding citing a MUST id, even if the source doc was tagged with an unrelated evidence_type (a "policy" doc claiming to satisfy a "register" MUST, etc.).

**Why:** workbook intake produces ONE `client_documents` row (the .xlsm file) feeding MANY leaves of DIFFERENT evidence_types simultaneously (asset_register / register / risk_register / revocation_record / etc.). The doc's single `evidence_type` value can't match all of them. The `cd.evidence_type = leaf.evidence_type` filter discarded every legitimate per-item finding when source-doc and leaf evidence_types disagreed.

**How to apply:** Phase-2 path now trusts `checklist_item_id` as authoritative — every item id is leaf-scoped, so by definition any approved per-item finding belongs to that leaf regardless of doc tagging. The cd.evidence_type filter stays on the Phase-1 fallback (still load-bearing there — the coarse path has no checklist_item_id to disambiguate). Comment in `_fetch_recognised_items` documents the asymmetry.

**Proof:** on Arion workbook (tagged risk_register at the doc level), Phase-2 recognition went from 0/N on every workbook-touched leaf to:
- A.5.9 asset_inventory: 5/6 MUSTs
- 6.1.2 risk_register: 4/6 MUSTs
- A.5.18 access_rights_register: 4/7 MUSTs
- A.5.26 incident_register: 2/5 MUSTs
- A.5.26 incident_closure_record: 3/8 MUSTs

**Related:** [[engine-agreement-suppression]] still hides the new reasoning at the proposal level when engine-NC == live-NC; tenant sees the delta only via `tenant_evidence_gaps`.
