---
name: feedback-phase-1-fallback-masks-gaps
description: "Engine's Phase-1 fallback in leaf_evaluators (coarse cd.evidence_type match → ALL leaf MUSTs satisfied) systematically OVERSTATES coverage. When per-MUST checklist_item_id bindings are added (workbook intake, leaf-scan), Phase-2 takes over and reveals the truer per-MUST gap picture — which can look like a posture regression but is actually the previous over-counting being exposed. Retire Phase-1 fallback; build for Phase-2."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When designing systems that have a "strict per-item" path and a
"lenient coarse" fallback for compliance recognition,
**investments that strengthen the strict path will inadvertently
expose gaps the lenient path was masking.** That's the system
becoming more honest, not the evidence regressing.

## The specific case

`rag/posture/leaf_evaluators.py:_fetch_recognised_items` runs:

  1. **Phase 2 (strict)**: `WHERE df.checklist_item_id = ANY(<leaf MUST ids>) AND df.status='present'` — per-MUST verification.
  2. **Phase 1 (lenient fallback)**: if Phase-2 returns 0 results, fall back to `WHERE cd.evidence_type = <leaf's evidence_type> AND df.control_ref = <control>` — and call **ALL** of the leaf's MUSTs satisfied if any doc of the right type exists.

Phase-1 was a Phase-1-era safety net for legacy findings with no
checklist_item_id binding. It significantly overstates coverage:
one uploaded "procedure" document makes every procedure-shape
leaf 100% satisfied without any per-MUST verification.

## What surfaces this

Adding checklist_item_id bindings via workbook intake or
leaf-scan flips a leaf from "Phase-1 fired and called it
satisfied" to "Phase-2 fires and shows the actual partial
coverage". Engine count drops, posture looks worse, tenant
sees a "regression".

But it isn't. The evidence is exactly what it always was. The
engine has just stopped pretending.

## How to apply

When auditing engine output for a tenant, look for cases where:

  - A leaf shows `satisfied=True` with empty `items_recognised`
    list — that's Phase-1 firing.
  - A leaf jumped from satisfied to partial after a workbook
    upload or leaf-scan run — that's Phase-2 taking over.

When designing new intake paths, **always populate
checklist_item_id**. Don't rely on Phase-1; it's a transitional
hack that should die. The backlog item "retire Phase-1
fallback" is the structural fix; until it ships, expect this
pattern to recur.

## Implication for tenant UX

A Phase-2-revealed regression can look like the system "got
worse" after a system improvement. Tenants need to understand:
the engine moved from a lenient view to an honest view. The
control wasn't actually MORE compliant before; the system was
less perceptive.

Communicate this clearly when the pattern hits — frame as
"the system used to overcount; now it counts honestly". Avoid
auto-approving Stage-2 proposals that *flip backward* under
this pattern. They're typically not progressions — they're
the lenient view being unmasked.

## Scar

2026-06-13 — A.5.18 leaf-scan validation. Added 15
checklist_item_id-bound findings via leaf-scan; engine
recomputed from OFI 1/4 → NC 0/4. The 15 approvals were real
audit-trail enrichment but the engine count "regressed"
because the previous "1 satisfied" was Phase-1 lenient on
3 of 4 leaves. Rejected the Stage-2 NC proposal to preserve
prior tenant judgment; documented the architectural finding
here.

## Related

- [[leaf-driven-scan-pilot-2026-06-12]] — where this finding
  was surfaced operationally on a second control
- [[feedback-intake-label-unreliability]] — sibling rule:
  per-MUST binding is the trustworthy signal, not coarse
  document-type labels
- [[leaf-evaluators-phase2-evidence-type-drop]] — earlier
  related work that dropped `cd.evidence_type` filter from
  Phase-2 specifically (Phase-1 still uses it)
- [[posture-writer-drop-fuzzy-match-2026-06-12]] — sibling
  case where evidence_type swap broke Phase-1 fallback;
  same architecture exposing weakness
