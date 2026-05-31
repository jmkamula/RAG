---
name: engine-agreement-suppression
description: "posture_loader.py:343 silently suppresses Stage-2 proposals when engine NC agrees with live NC; loses engine's 4-leaf reasoning; first observed cleanly in batch 4 A.5.26"
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

`posture_loader._persist_engine_proposals` skips proposal persistence when engine agrees with the live finding and there's no existing pending proposal:

```python
# posture_loader.py:343-344
if live_finding == posture and cur_status in ("none", None):
    continue
```

**Why it exists:** prevents the Stage-2 queue from flooding with ~80 auto-Comply rows where engine + intake already align. Useful suppression.

**Where it's lossy:** *NC-on-NC* agreement (and to a lesser extent OFI-on-OFI). The engine has structured 4-leaf reasoning (`'ALL: 0/4 children satisfied'`) that's strictly more informative than the legacy single-leaf gap_description. Suppressing the proposal hides the engine's structured view from both the Stage-2 queue and the LLM context — the tenant can no longer see *which* of the 4 sibling leaves is missing, only the legacy "drill not conducted" prose.

**First observed cleanly:** batch 4 (2026-05-31, [[curation-phase-b-batch-4-2026-05-31]]) on A.5.26. Live=NC, engine=NC at 0/4 → no proposal persisted → no Stage-2 surface → can't be eval-covered through LLM chat.

**Possible improvement (product call, not coded):**
- Keep the suppression for `Comply == Comply` agreement (engine adds nothing).
- Persist the engine reason for `NC == NC` and `OFI == OFI` agreement, even without raising it as a Stage-2 *proposal* — surface it as informational context. This would let the LLM access the 4-leaf detail without spamming the Stage-2 review queue.
- Schema change required: separate `engine_finding` + `engine_reason` (always populated when applicable) from `engine_proposal_finding` + `engine_proposal_reason` (only when divergent).

**How to apply:**
- When a future Phase B batch promotes a control where live posture is already NC (or OFI), expect the engine proposal to not surface through Stage-2. Verify the engine signature via `compute_engine_verdicts()` directly, and document the suppression in the batch memory.
- Eval cases need a non-LLM surface to lock these controls' 4-leaf shape. Currently no such surface in `tests/eval_suite.py` — would need to add one (e.g. unit-test pattern that inspects `compute_engine_verdicts()` output and asserts leaf count + signature).
- If product decides the suppression should be relaxed for NC/OFI agreement, the change is localised to `posture_loader._persist_engine_proposals` + the `posture_controls` schema.

Related: [[curation-phase-b-batch-4-2026-05-31]] for the originating context, [[hitl-two-stage-approval-design]] for the broader Stage-2 design intent the suppression serves.
