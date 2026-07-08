---
name: feedback-engine-should-not-clobber-tenant-na
description: "Engine's NC proposal can silently override a tenant's N/A declaration on the same control if a prior Stage-2 approval left engine_proposal_status='approved'; N/A must always dominate over engine derivations"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Surfaced 2026-07-08 on Arion: `A.7.2.7` (Joint Controllers) and
`A.7.3.10` (Automated decision-making rights) were declared N/A by
the tenant with clear scoping rationale ("no joint controller
arrangements", "no solely-automated decisions"). Both flipped to
NC on live posture (`posture_controls.finding='NC'`) despite active
`tenant | N/A | active` rows in `posture_assertions`.

Trace: earlier Stage-2 batch approval left
`posture_controls.engine_proposal_status='approved'` on both controls.
Engine kept re-proposing NC on subsequent runs. The reader's overlay
in `rag/posture_loader.py:_apply_engine_overlay` (line ~266) applies
the engine verdict whenever `engine_proposal_status='approved'` OR
the engine agrees with the live gap — with no exception carved out
for tenant N/A. So the "approved" flag from an unrelated prior action
kept the NC in place across engine reruns.

**Why:** tenant N/A is a scoping declaration — it says "this control
does not apply to us at all". Engine NC is a derivation over evidence
absence. When they disagree, tenant N/A must dominate: the engine
saw no evidence *because there shouldn't be any*. Currently, engine
can silently blow through N/A via the approved flag.

**How to apply:**

- The `_apply_engine_overlay` overlay logic (rag/posture_loader.py
  ~line 266) needs an early-continue when `row["finding"] == "N/A"`
  regardless of engine_proposal_status. Tenant N/A is not overridable
  by engine derivation.
- `_persist_engine_proposals` (further down in same file) should not
  write an engine proposal for a control whose live finding is N/A —
  or if it does write one, it must reset `engine_proposal_status` to
  `'proposed'` (not stay 'approved') so no old approval bleeds
  through.
- When a tenant declares N/A via a doc-upload trigger or profile
  edit, the tenant N/A write should also reset any prior engine
  proposal status on the row.

Related:
- [[tenant-must-overrides-v43-2026-06-23]] — per-MUST N/A already
  handles the finer-grained case; leaf-level N/A needs the same
  protection
- [[hitl-two-stage-approval-design]] — Stage-2 approval workflow
  where the "approved" flag comes from
