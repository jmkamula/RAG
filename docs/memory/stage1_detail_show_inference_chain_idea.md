---
name: stage1-detail-show-inference-chain-idea
description: "FUTURE: surface the cross-framework inference chain (inferred_from_control_ref + standard) in the Stage-1 detail panel so users approving GDPR findings see which ISO finding they were derived from. Proposed 2026-05-25 during initial HITL UI testing."
metadata: 
  node_type: memory
  type: project
  originSessionId: 05fd0622-fbff-4999-9132-e4622a40b0f2
---

User proposal 2026-05-25 (after [[stage1-contract-change-path-a-2026-05-25]] shipped and they began testing the new Stage-1 UI):

> "Can we include the ISO 27001 or whatever other standard it was inferred from in the details?"

**Why:** Today the Stage-1 detail panel for an inferred GDPR finding shows only the propagated excerpt. The user can't tell from the UI that, say, `Art.32` came via xfw_bridge from `A.5.23` in their Information Security Policy. They effectively reviewed the same evidence twice (once under ISO, once under GDPR) without realising the second was a derivation of the first. Surfacing the provenance lets them spot when a derivation is questionable for that specific GDPR article even though the source ISO finding is solid.

**How to apply:** When implementing, extend `GET /api/v1/stage1/queue/{control_ref}` to return `inferred_from_control_ref`, `inferred_from_standard_id`, `inference_source` per finding (already on `document_findings`). Update `selectStage1` in `static/arioncomply.html` to render an "Inferred from" line when those columns are non-NULL — e.g. `Inferred from ISO27001:2022 A.5.23 (via xfw_bridge)`. Consider a small icon/link to jump to the source ISO control's pending findings.

**Out-of-scope refinement to consider:** if 100% of pending GDPR findings for a control are inferred from the SAME source ISO control, the UI could merge the cards visually or offer a single "approve both" action so the user doesn't re-evaluate the same evidence twice. Avoids duplicate work when the user has already approved the ISO side.

**Data available right now:**
- `document_findings.inferred_from_control_ref` (e.g. 'A.5.23')
- `document_findings.inferred_from_standard_id` (e.g. 'ISO27001:2022')
- `document_findings.inference_source` (e.g. 'xfw_bridge')

Confirmed during 2026-05-25 testing session: 24 of 24 pending GDPR findings are `inference_source='xfw_bridge'`. None are directly extracted — current Arion tenant docs don't cite GDPR articles, so all GDPR coverage is bridge-derived.

Related: [[stage1-contract-change-path-a-2026-05-25]], [[engine-to-posture-controls-wiring-fix]].
