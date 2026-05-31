---
name: curation-phase-b-batch-4-2026-05-31
description: SHIPPED 2026-05-31 — A.5.25/A.5.26/A.5.27 operational_process 4-leaf incident triage family; first batch where engine agreement with live posture suppressed Stage-2 surfacing (A.5.26); review freshness 180d for A.5.25 + A.5.26
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

Fourth Phase B bulk batch — three ISO A.5 incident-family controls promoted from single-leaf to operational_process 4-leaf in one pass. All three controls are clean procedure-shaped (unlike batch 3 which had template + review-record + policy variants), so the spine applies without primary-leaf adaptation; only the lifecycle-end slot varies per control.

**Spine application (uniform operational_process, lifecycle-end semantic varies):**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.25 | event_assessment_procedure | event_triage_log | triage_program_review **(180d)** | triage_decision_record |
| A.5.26 | incident_response_procedure | incident_register | ir_program_review **(180d)** | incident_closure_record |
| A.5.27 | lessons_learned_procedure | lessons_register | lessons_program_review (365d) | improvement_action_record |

**Cross-control linkages** (encoded as MUST items, not graph edges):
- A.5.25 triage_decision_record `dec_handoff` → A.5.26 incident_register
- A.5.26 incident_closure_record `cls_lessons_handoff` → A.5.27 lessons_register
- A.5.27 lessons_register `reg_source_incident` → A.5.26 incident_register (back-pointer)

**Why 180d on A.5.25 + A.5.26:** detection landscape moves fast (new sources, attack patterns, false-positive calibration); IR readiness erodes between exercises and incidents. Annual cadence is too loose. A.5.27 lessons program stays 365d because lessons accumulate slowly and the meta-review of the lessons program doesn't need to chase the same operational tempo.

**Engine signatures on Arion (post-load):**
- A.5.25 → engine NC at 0/4 (live was Comply); status=proposed → Stage-2 surface visible
- A.5.26 → engine NC at 0/4 (live also NC) → **NOT proposed, suppressed**
- A.5.27 → engine NC at 0/4 (live was Comply); status=proposed → Stage-2 surface visible

**The A.5.26 suppression — first batch to encounter it cleanly:**
`posture_loader.py:343` skips proposal persistence when `live_finding == posture and cur_status in ("none", None)`. Comment: *"when the engine agrees with the tenant's live posture and there's no existing pending proposal to refresh, there's nothing for Stage-2 to review. Avoids flooding the queue with auto-Comply rows for the ~80 controls where engine + intake already align."*

This means the engine's 4-leaf gap analysis ("0/4 children satisfied") is computed in memory by `compute_engine_verdicts()` but never persisted to `posture_controls.engine_proposal_reason`, never reaches the LLM context, never surfaces to the tenant. The tenant sees only the legacy single-leaf gap_description ("incident response drill not conducted Q1 2025") — which is technically still correct but loses the structured "you have 0 of 4 sibling artefacts" view.

**Product implication (not fixed in this batch — flag for product owner):**
When engine agrees with live, the tenant loses access to the engine's more granular reasoning. The current suppression treats agreement as "nothing to do" but for *NC-on-NC* agreement specifically, the engine actually has more detail (4 unsatisfied leaves) than the live finding (one drill not run). For OFI-on-OFI or Comply-on-Comply agreement the suppression is fine. Worth considering: suppress agreement only when the live finding is `Comply` (where engine adds nothing new), but always surface engine reasoning when live is `NC` or `OFI` (engine often has additional structural detail). Out of scope here.

**Eval coverage:** Cases 61 + 62 added for A.5.25 + A.5.27 via the standard Stage-2 list_one surface. A.5.26 deliberately NOT eval-covered — its 4-leaf shape is verified at commit time via direct `compute_engine_verdicts(pg, neo, TENANT)` inspection (returns `'NC'`, `'ALL: 0/4 children satisfied'`, `leaves=4`) but doesn't surface through any LLM chat path. Future eval surfaces (e.g. a unit-test pattern outside the LLM chat surface) could lock A.5.26 explicitly. Logged as TODO.

**Eval result: 58/60 → 60/62 PASS** (the run that motivated commit showed 61/62, but #24 stochasticity means baseline target stays 60/62 with #24 + #25 known-stale).

**Loader behaviour:** 0 MUST + 2 SHOULD stale edges pruned (the 2 SHOULDs are old A.5.26:classification_ref + A.5.26:evidence_ref — renamed into MUSTs as classification_link + evidence_collection on the new procedure leaf). 2 orphan items pruned. Clean.

**Authority — ISO 27002:2022:**
- § 5.25 implementation guidance (categorisation, decision criteria, correlation, competent personnel access, who-may-need-to-be-informed)
- § 5.26 items a–i (containment, evidence, communication, coordination, recovery, action logging, communication, root-cause resolution, closing)
- § 5.27 items a–f (strengthen controls, update risk, update plans, update training, recurring patterns, root-cause typing)

**Phase B remaining (post-batch tally):**
- ISO 27001: ~94 thin single-leaf controls remaining (was 97 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 9 controls now (A.5.18 calibration + supplier 4-pack + A.5.23 + incident 3-pack)
- Spine model: unchanged. The "engine-agreement suppression" surface gap is a *product/eval-coverage* observation, not a spine question.

**Next-likely candidates:**
- A.5.7 threat intelligence (procedure-shaped, op_process or policy_program — depends on whether the artefact is a *policy* or a *procedure*; org typically has a small threat intel program with feed register + cadence)
- A.5.28 evidence handling (single-leaf, procedure-shaped, op_process; tightly coupled to this batch — could have been included as a 4-pack but skipped because not in the user's scoped list)
- Bulk policy_program siblings still pending (A.5.1 master InfoSec policy)
