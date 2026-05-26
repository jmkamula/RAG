---
name: stage1-detail-show-inference-chain-idea
description: "SHIPPED 2026-05-26: Stage-1 detail panel now surfaces the inference chain (inferred_from_control_ref + standard) plus labeled Evidence/Confidence chips with a gloss explaining the vocabulary."
metadata:
  node_type: memory
  type: project
  originSessionId: 05fd0622-fbff-4999-9132-e4622a40b0f2
---

**Status: SHIPPED 2026-05-26** (working tree, not yet committed at time of writing).

User asked back-to-back on 2026-05-25 then 2026-05-26: (1) "Can we include the ISO 27001 or whatever other standard it was inferred from in the details?" (2) "include the referenced framework and i'm not sure i understand partial and medium". Both addressed in the same edit pair.

**What shipped**
- `rag/posture/stage1_review_chat.py:154` — `list_pending_for_control` SELECT extended with `inferred_from_control_ref`, `inferred_from_standard_id`, `inference_source` from `document_findings`. Purely additive; existing callers (`render_stage1_answer` in the chat path) ignore the new keys.
- `static/arioncomply.html` `selectStage1`:
  - Adds one-line gloss above the findings explaining `Evidence` (missing/partial/present = doc coverage) vs `Confidence` (low/medium/high = extractor certainty). User was confused seeing the raw chips with no label.
  - Relabels the two chips inline: `Evidence: <pill>` / `Confidence: <pill>`.
  - When `inferred_from_control_ref` is non-NULL, renders a dashed-border row under the excerpt: `↩ Inferred from <standard · control_ref> via <source>` (e.g. `ISO27001:2022 · A.5.12 via xfw_bridge`).

**Verified on real data:** Art.10 pending finding (the one the user was looking at) returns `inferred_from_control_ref=A.5.12, inferred_from_standard_id=ISO27001:2022, inference_source=xfw_bridge`. All 24 pending GDPR findings on the Arion tenant carry `inference_source=xfw_bridge` — none directly extracted, since the tenant docs don't cite GDPR articles.

**Restart gotcha:** HTML edit is live without restart (FastAPI StaticFiles reads disk per-request); the SQL column addition requires API restart to flow through `/api/v1/stage1/queue/{control_ref}`. User accepted restart despite eval being 38/39 (case #25 failing pre-edit, unrelated — see [[stage1-contract-change-path-a-2026-05-25]]).

**Out-of-scope refinement not yet shipped:** if 100% of pending GDPR findings for a control are inferred from the SAME source ISO control, the UI could merge the cards visually or offer a single "approve both" action. Still worth doing — would avoid duplicate review work.

**Eval coverage:** none yet. Per [[feedback-eval-with-each-feature]] this needs a case. The Stage-1 surface is HITL-only (no RAG entry point), so the regression test would have to hit the REST endpoint and assert the new fields appear in the JSON response. Pending.

Related: [[stage1-contract-change-path-a-2026-05-25]], [[engine-to-posture-controls-wiring-fix]], [[hitl-two-stage-approval-design]].
