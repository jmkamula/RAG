---
name: feedback-stage1-detail-ux
description: "User UX preferences for the Stage-1 / Stage-2 detail panel: leaf grouping + canonical title yes; LLM crafting no; standard text hidden by default behind a disclosure"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

User reviewed the Stage-1 detail surface multiple times on 2026-06-06 and settled on three concrete UX rules. These apply equally to the Stage-2 detail panel (shared element via `populateCanonicalSummary` + leaf-grouping renderer).

## Rules

1. **Group findings by sheet → leaf → MUST** in the detail list. Showing only the column excerpt (`sheet 'Audit Log' col 'Date'`) without saying WHICH MUST or WHICH LEAF the column satisfies feels repetitive and unintelligible. The same column legitimately satisfying multiple MUSTs on sibling leaves needs to LOOK intentional — the leaf header is what explains why.

2. **Show the canonical control title** above each detail panel (e.g. "Internal audit" for 9.2). Don't assume the reader recognises ref-only labels.

3. **Do NOT show the full standard text by default.** Some controls (6.1.3, 5.x policy clauses) carry multi-paragraph normative text that dominates the panel and pushes the actual finding off-screen. Use a native `<details>/<summary>` disclosure ("Show standard text") collapsed by default.

**Why:** the detail panel is a per-row review surface — the reviewer is approving / rejecting individual findings, not learning the standard. The title plus a structured per-finding list is enough context.

**How to apply:** any future detail-surface work (new evidence types, new HITL stages) should preserve title-only headers + leaf-grouped rows. If a richer narrative is needed, treat description / standard text as ON-DEMAND (disclosure, modal, sidebar) rather than always-visible.

## LLM crafting was explicitly rejected

Considered using an LLM to rewrite per-row finding labels into natural-language descriptions ("Arion's Audit Log strongly captures the basics — auditor, date, scope per audit. The auditor-grade fields aren't surfaced as discrete columns…"). User decision: keep the LLM out for now and make the deterministic rendering more readable. Reasons that drove the decision:

- Per-row LLM rewrites add 2-5s latency per detail view (high-frequency surface).
- Hallucination risk on audit-critical rendering — the reviewer is making approve/reject decisions on the YAML's column→MUST bindings, not on LLM prose.
- Auditor provenance prefers deterministic: "YAML bound column X to MUST Y" is auditable; LLM phrasing isn't.

A one-shot LLM summary header (single call per detail open, narrating the whole control's posture) remains reversible future work if it would add value. Don't bring it back without an explicit ask.

## Post-dejargonize note (2026-07-01)

Additional Stage-1 detail rules ratified via the 2026-07-01
de-jargonize pass, folded into the same surface without
contradicting the three rules above:

  - Group header ref chip shows the short control ref
    ('A.5.15') rather than the full `leaf_id` machine form
    (`req:A.5.15:access_control_policy`). Full id still lives in
    `data-` attributes for admin traceability.
  - `standard_id` humanized (`ISO27001:2022` → `ISO 27001:2022`).
  - `inference_source` slugs humanized (`workbook` →
    "workbook upload", `leaf_scan` → "prior finding") via the
    client-side `humanizeSource()` helper.
  - Item-id chip beside a MUST shows just the last slug segment
    (`boundaries`) not the full `item:X:Y`.

The "no LLM crafting" rule still holds — deterministic rendering
via humanizer helpers, not per-row LLM rewrites.

## Related

- [[workbook-intake-corpus-v1-complete]] — the structured data the detail surface renders
- [[dejargonize-ux-pass-2026-07-01]] — the surface-wide natural-
  language pass; ratifies these rules across every detail panel.
