---
name: stage1-engine-kick-after-batch
description: "SHIPPED 2026-06-08 (8ed827e): Stage-1 batch approval/no-row paths now auto-kick the engine sweep so Stage-2 reflects new evidence without a separate manual load_posture call."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Closes the long-standing follow-up flagged on
[[stage1-contract-change-path-a-2026-05-25]]: *"writer engine-kick
still pending"*. Before this fix, a Stage-1 batch approval only
marked `document_findings.review_status = 'approved'`; the engine
verdict stayed stale until someone called `load_posture()` separately.
The Access Management Process upload session on 2026-06-08 surfaced
the user-visible symptom: 12 approved findings, zero Stage-2 movement
until a manual sweep.

## What ships in `rag/posture/stage1_review_chat.py`

`_kick_engine_sweep(pg_conn, tenant_id)` helper (lines ~31):
- Imports `load_posture` lazily; calls it on the same pg_conn.
- After the sweep, counts `posture_assertions` rows with
  `status='pending' AND set_by='engine'` for the tenant and returns
  the integer.
- Catches all exceptions, rolls back its own conn state on failure,
  returns `-1`. **Never raises.** A sweep failure must NOT undo the
  approvals that just committed — they're independent.

Wired into both approve paths:
- `approve_findings_by_ids` (UI per-id path) — post-commit, returns
  `stage2_pending: N` in the response.
- `approve_findings_for_control` (chat whole-control path) — same
  wiring; also wires the `no_posture_row` early-return so the
  defensive path doesn't skip the sweep.

**Reject paths intentionally NOT wired** — current scope is approval
only. If rejection-time engine re-evaluation becomes a tenant ask,
add `_kick_engine_sweep` after the two reject commits (lines ~468
and ~649).

## Trade-offs

- **Latency cost**: every Stage-1 batch now pays one full engine
  sweep (~500ms-2s on Arion's posture surface of ~177 controls).
  Per-batch, not per-finding — bulk approval doesn't multiply.
- **Concurrency**: two concurrent batches on the same tenant trigger
  two sweeps. They're idempotent (engine assertions are upserted by
  control_ref), but waste compute. Acceptable for current per-tenant
  click-through HITL volume.
- **Connection state**: helper runs on the same conn the approval
  used. If the engine sweep itself raises, we rollback that conn
  (the approval is already committed, so the rollback is a no-op for
  the approval). New PostgresSaver patterns may need re-evaluation.

## Verification

End-to-end smoke: helper alone returns 7 (current pending count) on
Arion. Eval 197/198 PASS — only #21 LLM-stochastic.

Eval cases ratcheted in same session (commit 94bfaae):
#42 (A.8.2), #69 (A.5.16), #70 (A.5.17), #129 (A.8.5), #165 (Art.21),
#168 (Art.18). All 6 previously locked-in `"already approved" / "NC"`
(Phase C batch 1 mass-approval state on 2026-06-02). Today's Access
Mgmt Process upload + Stage-1 approval + auto-engine-kick created
fresh `OFI` proposals on each, so the eval shape moved to
`"engine proposes" / "OFI" / "1/4 children satisfied"` (1/4 because
each upload only satisfies 1 leaf of the 4-leaf multi-leaf spec).

## Related

- [[stage1-contract-change-path-a-2026-05-25]] — the contract change
  this closes the follow-up on.
- [[posture-engine-alignment-plan-2026-05-22]] — Phase D engine-kick
  was always implied; finally landed.
- [[hitl-two-stage-approval-design]] — the two-stage design now flows
  in one user action when the user wants it to (Stage-1 batch →
  engine sweep → Stage-2 entry visible).
