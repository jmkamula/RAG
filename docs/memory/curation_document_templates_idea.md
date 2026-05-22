---
name: curation-document-templates-idea
description: "Forward idea (2026-05-22) — ship template documents alongside EvidenceRequirement curation, so tenants get a starting draft that already covers the MUST items"
metadata: 
  node_type: memory
  type: project
  originSessionId: f7c71005-682b-4044-b08a-31f8be272dc2
---

**Idea (raised 2026-05-22):** as part of [[posture-engine-alignment-plan-2026-05-22]] Phase B (curating Neo4j), consider shipping document templates alongside each `EvidenceRequirement`.

**Concept:** for every leaf, also publish a template artifact (Markdown or docx) whose structure already covers the leaf's MUST items. A tenant without an existing document of that type can clone the template, customise it, and upload it. The MUST items are pre-aligned by construction, so the extractor's recognition + the engine's evaluation work out of the box.

**Why:** closes the human-in-the-loop loop on our side. We don't just say "we expect a remote working policy with these 6 elements" — we hand the tenant a starting draft. Useful for smaller orgs without an existing compliance documentation base. Per [[human-in-the-loop-positioning]], we help rather than judge.

**How to apply:** Not in scope for the active alignment plan (Phases A-D). Revisit after Phase D ships. When extending `EvidenceRequirement` in Phase A, leave room for an optional `template_ref` field (or similar) so the model doesn't have to be reshaped later.
