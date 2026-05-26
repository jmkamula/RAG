---
name: engine-proposes-for-all-curated-specs
description: "SHIPPED 2026-05-26: removed the len(leaves)<=1 gate in posture_loader so the engine proposes a Stage-2 verdict for every curated control where it disagrees with the live finding, not just multi-leaf or derives_from specs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 23cb7b33-d854-4985-9f9a-c02de86209a1
---

**Status: SHIPPED 2026-05-26.**

User observation that triggered the change: on the dashboard A.5.3 showed Comply with one narrow evidence excerpt ("PII two-stage approval") and the engine's view (looking for a "Segregation of Duties Matrix" leaf, 0/1 satisfied) was nowhere in the UI. User pointed out: "Stage-1 accepts the extraction not the posture. The engine should still propose posture regardless."

**Root cause:** `_persist_engine_proposals` and `_apply_engine_overlay` in `rag/posture_loader.py` both had a gate:
```python
if len(verdict.leaves) <= 1 and not verdict.derived_from:
    continue
```
Rationale (from the old comment): "Single-leaf specs are skipped — posture_controls.finding already represents their state." That was valid when Stage-1 mutated posture; under [[stage1-contract-change-path-a-2026-05-25]] (Path A, 2026-05-25), Stage-1 only confirms evidence, so the live finding can legitimately differ from the engine's leaf-evaluator view. The gate silently hid every engine-vs-intake disagreement on single-leaf controls.

**Fix:** removed the gate in both places. The engine now proposes a Stage-2 verdict for every curated spec with a determinative posture (NC/OFI/Comply/N/A). To avoid flooding Stage-2 with no-op auto-Comply rows, `_persist_engine_proposals` got a new short-circuit: skip when `live_finding == verdict.posture AND engine_proposal_status IN ('none', NULL)`. Idempotency check on `(engine_proposed_finding, engine_proposal_reason)` still runs after.

**Effect on Arion tenant:** 94 new engine proposals written on the next load — most are ISO 27001 single-leaf controls where intake confirmed Comply but the engine's leaf evaluator can't match the specific artifact (e.g. "Segregation of Duties Matrix" for A.5.3). Combined with [[engine-nc-at-zero-satisfied]] (engine emits NC at 0/N), many of these proposals are NC, which is the engine's strict view of curation expectations.

**Implication for the tenant:** real curation conversation surfaced. The tenant must decide per control whether:
- The narrow excerpt (e.g. "PII two-stage approval") satisfies the broader control (Segregation of duties) — approve engine OFI/NC if no, reject if you accept the narrower interpretation, or update curation to broaden the leaf evaluator's match.
- The engine's specific artifact expectation ("Matrix" not just any policy text) is too rigid — adjust the FulfilmentSpec / leaf evaluator.

**Eval impact:** running suite to check for regressions; case 33 (A.5.1 OFI) and 41 (A.5.30 Comply) should still pass since live findings haven't changed (only new proposals exist, in 'proposed' status — overlay only flips live on 'approved'). To be re-verified.

**Not done:** the leaf-evaluator strictness — many curated leaves expect specific document titles (e.g. "Segregation of Duties Matrix") rather than capability-level evidence. That's a curation-quality issue separate from the engine→Stage-2 wiring. Worth a future review.

Related: [[stage1-contract-change-path-a-2026-05-25]], [[engine-nc-at-zero-satisfied]], [[engine-to-posture-controls-wiring-fix]], [[hitl-two-stage-approval-design]].
