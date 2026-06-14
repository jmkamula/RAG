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

## Retirement shipped

2026-06-13 (same session) — Phase-1 fallback block deleted from
`rag/posture/leaf_evaluators.py:_fetch_recognised_items`. Pre-flight
survey on Arion showed 0 leaves currently Phase-1-satisfied (the
workbook intake + leaf-scan investments had already moved everything
to Phase-2 organically). Eval suite caught the 3 partial-evidence
cases that had encoded the lenient view (#55 A.5.15, #60 A.5.23,
#75 A.5.34, all asserting "1/4 children satisfied" via the policy
leaf's Phase-1 match); the cases were re-authored to acknowledge the
honest 0/4 output and the `partial_evidence` tag dropped. Function
signature kept (`evidence_type`, `control_ref` now unused but
preserved for caller symmetry).

## Validated at scale — 35-control Phase-1 surge resolved 2026-06-14

The pre-flight survey was too narrow. It counted "leaves currently
Phase-1-satisfied" but missed the upstream effect: many controls
were live=OFI (set via prior approvals) where the engine's OFI view
had been backed by Phase-1 satisfying at least one leaf. After
retirement, those controls' engine verdicts flipped to NC, producing
35 Stage-2 "OFI→NC" proposals visible to the tenant.

Recovery attempt: authored leaf-scan catalogs for all 35 controls
(batches 8-10, ~92 leaves, ~700 MUSTs), ran scan across all 35.
Result: 18 per-MUST back-bindings on 9 of 35 controls. Even after
approving all 18, NO control reverted to OFI because no leaf
reached full-MUST satisfaction — best case was 2/7 MUSTs bound on
A.5.15:access_control_policy.

This confirmed the architectural prediction: Phase-1 was crediting
1 finding as 8/8 because the doc matched evidence_type; the real
per-MUST evidence on Arion was 1-2/N for every flipped leaf. The
NCs are legitimate gaps the standards (ISO 27002:2022 + GDPR)
articulate but Arion's corpus doesn't.

Tenant accepted all 35 NCs as the honest posture. Live distribution:
167 NC / 10 OFI / 0 Comply / 0 N/A on 177 evaluable controls.

Insight: when retiring a lenient fallback, the pre-flight survey
must measure not just "currently satisfied via fallback" but
"controls whose OFI verdict depends on the fallback satisfying
≥1 leaf". The latter is the actual blast radius. For future
retirement of a lenient path, instrument the engine to log which
leaves' satisfaction depend on the lenient signal vs the strict
one, then count controls where every satisfied leaf depends on
the lenient path — that's the at-risk count.

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
