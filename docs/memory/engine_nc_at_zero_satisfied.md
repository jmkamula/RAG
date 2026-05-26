---
name: engine-nc-at-zero-satisfied
description: "SHIPPED 2026-05-26: fulfilment engine now emits NC (was OFI) when zero children are satisfied. Reviewer approves or rejects the NC proposal in Stage-2 like any other verdict."
metadata: 
  node_type: memory
  type: project
  originSessionId: 23cb7b33-d854-4985-9f9a-c02de86209a1
---

**Status: SHIPPED 2026-05-26.**

Prior behaviour: `_compose_posture` in `rag/posture/fulfilment_engine.py` only ever emitted `Comply` / `OFI` / `N/A`. Anything that wasn't fully satisfied became OFI, which collapsed the distinction between "1/N satisfied (partial coverage)" and "0/N satisfied (nothing at all)". NC was reserved for explicit human determination, but in practice there was no UI path to set it — Stage-2 reject just refuses the proposal, doesn't override, and Stage-1 stopped mutating posture per [[stage1-contract-change-path-a-2026-05-25]].

User asked 2026-05-26: "why is it OFI if none is processed?" Decision: engine should propose NC at 0/N and let the tenant approve or reject in Stage-2 — same review flow as OFI, no new UI affordance needed.

**What changed**
- `_compose_posture` now emits three tiers per op:
  - `ALL`: all satisfied → Comply; none satisfied → NC; otherwise OFI
  - `ANY`: any satisfied → Comply; otherwise NC
  - `AT_LEAST_N`: ≥threshold → Comply; zero → NC; otherwise OFI
- Empty-outcome branches (`had_derivation_NA`/vacuous-Comply) unchanged. Those mean "0 of N tried" doesn't apply — the dependencies were all N/A or gated off, which is a different signal.

**Downstream wiring** (already in place, no change needed):
- `posture_controls.engine_proposed_finding` CHECK constraint already allows NC (db/schema_v24_hitl_two_stage.sql:104-105).
- `_persist_engine_proposals` (posture_loader.py:260) writes any non-(UNKNOWN/deferred/NotApplicable) posture, including NC.
- `_apply_engine_overlay` (posture_loader.py:225) writes the engine verdict into the in-memory posture row only if `engine_proposal_status='approved'` — so NC proposals don't preempt the live finding until the reviewer signs off.
- Stage-2 chat surface lists/approves/rejects NC same as OFI (no finding-value filter).

**Observed effect on Arion tenant** (post-restart):
- Art.5 family (Art.5, 5.1, 5.1.a–f, 5.2): flipped OFI→NC, `engine_proposal_status` reset to `proposed`. All 0/N because none of the GDPR principles have satisfied evidence.
- Art.6: new OFI proposal (1/2 satisfied via A.5.34).
- Art.16, Art.24, Art.25, Art.32: already-approved; unchanged at OFI because 1/N satisfied.

**Eval coverage:** case 40 (`what is our posture on Art.5?`, must_contain=["NC","Art.5"]). Originally written against the Stage-2 list surface, but that was order-dependent: the consultant approved the Art.5 NC proposals via the UI during initial testing, so the queue drained. Rewrote on 2026-05-26 to assert the live posture after approval — the engine→approval→live-finding chain end-to-end, resilient to queue churn.

**Known eval interaction (follow-up):** case #25 (`is GDPR Art.5 a non-conformity?`) has `must_not_contain=["Art.5 is a non-conformity"]` per the old Layer-2 anti-hallucination contract. With Art.5's live finding now legitimately NC (engine emit + reviewer approve), that assertion is obsolete. User flagged #25 for separate cleanup; the engine NC ship date is the trigger for that cleanup. Don't touch #25 inside engine-NC commits — handle as a deliberate contract-update review.

**Open question for later:** the `had_derivation_NA` empty-outcomes case stays OFI (existing comment defends it: parent applies but every implementation route is N/A — curation incompleteness). If a user wants NC there too, revisit; but the semantics differ from "tried 2 things and 0 succeeded."

Related: [[hitl-two-stage-approval-design]], [[engine-to-posture-controls-wiring-fix]], [[stage1-contract-change-path-a-2026-05-25]].
