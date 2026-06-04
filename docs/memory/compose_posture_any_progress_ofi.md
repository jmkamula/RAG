---
name: compose-posture-any-progress-ofi
description: "SHIPPED 2026-06-04: _compose_posture promotes control to OFI when any leaf has items_recognised>0 (was: NC required all leaves to be fully satisfied for OFI). NC stays only when ZERO evidence anywhere. Dual of [[engine-nc-at-zero-satisfied]]."
metadata: 
  node_type: memory
  type: project
  originSessionId: b7702385-93e8-4fb5-8bcc-881816acb712
---

SHIPPED 2026-06-04 — composition rule change in `rag/posture/fulfilment_engine.py`.

## Rule

The prior rule was: a leaf's binary `satisfied` flag (True only if all MUSTs recognised AND fresh) drove control posture. `_compose_posture` saw `outcomes: list[bool]` and:
- All True → Comply
- Zero True → NC (per [[engine-nc-at-zero-satisfied]])
- Some True → OFI

Problem: a *partial* leaf (e.g. 5/6 MUSTs recognised) counted as **unsatisfied** at the leaf gate. A.5.9 with leaves 5/6 + 0/4 + 0/5 + 0/5 had zero satisfied → control NC. Workbook intake's contribution was invisible at the control posture layer.

New rule: a parallel `progress: list[bool]` runs alongside `outcomes`. Progress = True iff the child has ANY evidence (leaf with ≥1 items_recognised, OR sub-verdict at Comply/OFI). `_compose_posture` uses it to distinguish "no evidence anywhere" (NC) from "some evidence, gaps remain" (OFI).

For ALL / AT_LEAST_N ops:
- All outcomes True → Comply (unchanged)
- Zero outcomes AND no progress → NC (still — dual of [[engine-nc-at-zero-satisfied]])
- Otherwise → OFI (broader than before)

ANY op unchanged (zero outcomes → NC; any True → Comply).

## Why

User flagged that workbook intake landed but NC count didn't move (168 → 168) — controls "stuck" at NC despite material progress at the leaf level. Without this rule change, every control with partial-leaf evidence would stay NC until ALL leaves are fully satisfied, which requires multiple evidence-source channels (workbook + procedure docs + review records + discovery records) to converge. Hard to demonstrate progress incrementally.

## How to apply

When recomputing posture after evidence changes, watch for controls flipping NC→OFI even with no fully-satisfied leaves. Reason text now reads "X/Y children satisfied (Z with partial evidence)" — the Z count is the key signal that the new rule fired.

## Impact on Arion (2026-06-04 sweep)

Engine NC: 168 → 150 (18 controls flipped to OFI). 19 new Stage-2 pending proposals (one Comply→OFI extra). 4 ISO controls direct from workbook (A.5.9, A.5.18, A.5.26, 6.1.2); 15 GDPR articles via DerivedSpec cascade (Art.5, Art.5.1.x, Art.6, Art.16, Art.17, Art.24, Art.25, Art.32).

8 eval cases needed updating (`tests/eval_suite.py`) — they were locked to the prior "already approved + NC" state on these specific controls. Re-asserted to expect "engine proposes / OFI / partial evidence" since the new composition rule rightfully re-proposes when reasoning changes materially.

## Side fix

`_build_reason` extended with the same `progress` parameter. Reason string now appends `"(N with partial evidence)"` when any child has progress without satisfaction. Useful audit signal.

## Related

- [[engine-nc-at-zero-satisfied]] — the prior rule this change rounds out. NC at zero stays; the new rule fills in the "some evidence" half.
- [[engine-agreement-suppression]] — still hides reasoning when engine verdict matches live. Less impactful now that the engine more often produces verdicts that DIFFER from live (NC→OFI).
- [[leaf-evaluators-phase2-evidence-type-drop]] — the prerequisite that lets workbook findings actually reach the leaf evaluator and provide `items_recognised`.
