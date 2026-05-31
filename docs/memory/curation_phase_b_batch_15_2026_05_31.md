---
name: curation-phase-b-batch-15-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.29 single-control batch (info security during disruption) operational_process 4-leaf with plan-as-primary; HYBRID activation_record covers BOTH real disruptions AND scheduled tests via type field (position 17); fourth consecutive SHOULD-promotion (test_schedule); new degradation_levels MUST encodes \"appropriate level\" auditor concern"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Fifteenth Phase B bulk batch — single-control: A.5.29 (Information security during disruption) promoted from single-leaf to operational_process 4-leaf with **plan-as-primary** variant.

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.29 | continuity_security_plan **(plan)** | disruption_scenario_register | continuity_program_review **(180d)** | per-activation plan_activation_record |

**Plan-as-primary variant — confirmation of pattern:** the operational_process spine accommodates any artefact form as primary. Prior variants:
- A.5.14 = policy (batch 11)
- A.5.20 = agreement_template (batch 3)
- A.5.22 = review_record (batch 3)
- A.5.23 = policy (batch 3)
- A.5.29 = **plan** (batch 15)

The spine remains stable; only the primary-leaf evidence_type varies based on the control's natural artefact form.

**Cross-control linkages:**
- plan `scenarios` (MUST) → A.5.7 threat intel + A.5.21 supplier
- plan `communication` (MUST) → A.5.24 IR framework
- plan `restoration` (MUST) → A.5.30 ICT readiness (companion control, candidate for batch 16)
- plan `third_party` (SHOULD) → A.5.22 supplier review
- register `reg_in_scope_ctrls` (MUST) → A.5.9 asset register
- register `reg_recovery_target` (SHOULD) → A.5.30 RTO/RPO
- record `act_incident_link` (SHOULD) → A.5.26 incident register
- record `act_lessons_feed` (SHOULD) → A.5.27 lessons register

**Why 180d on the program review:** disruption landscape shifts (new cyber threats, new supplier dependencies, new infrastructure). Same volatility family as A.5.24 IR planning (180d, batch 14), A.5.25/A.5.26 incident family (180d, batch 4).

**Plan_activation_record (position 17 in lifecycle-end catalogue): HYBRID variant.** Covers BOTH real disruptions AND scheduled tests via a `act_type` field. This is genuinely new — distinct from:
- A.5.24 exercise_record (drills ONLY — never real incidents)
- A.5.26 incident_closure_record (real incidents ONLY — never drills)
- A.5.29 activation_record (**BOTH** — type field distinguishes)

The hybrid shape is appropriate because A.5.29's plan literally has the same activation regardless of trigger: drop to fallback, maintain appropriate level, restore. Whether the trigger was real or drill, the plan ran identically. The hybrid record captures both consistently.

**New MUSTs over the legacy single-leaf:**
- `degradation_levels`: encodes "appropriate level" = graceful degradation explicitly. Risk-tiered which controls drop to compensating, which must hold at full. **One of A.5.29's most-tested auditor concerns** — auditors specifically ask "if X fails, what's the degraded acceptable state?"
- `activation_authority`: who declares the plan active; who declares it stood down; criteria for each
- `test_schedule`: promoted from SHOULD (fourth consecutive SHOULD-promotion)

**SHOULD-promotion pattern — FOURTH consecutive batch:**
- Batch 12 A.5.16: `service_accounts` SHOULD → MUST (id preserved)
- Batch 13 A.5.17: `mfa` SHOULD → MUST (id preserved)
- Batch 14 A.5.24: `tested` SHOULD → `exercise_cadence` MUST (renamed)
- Batch 15 A.5.29: `test_schedule` SHOULD → MUST (id preserved)

**Test-cadence common theme** in batches 14+15: both BCP-adjacent controls had untested-plan SHOULDs that are now MUSTs. The pattern: where a plan's effectiveness depends on being exercised, the test cadence is load-bearing, not optional. Likely applicable to A.5.30 (next candidate) as well.

**Engine signature on Arion (post-load):**
- A.5.29 → NC at 0/4 children satisfied (plan 0/8 + register 0/7 + review 0/7 + record 0/8)
- Live was Comply (hand-entered finding citing BCP + GDPR/privacy compliance during recovery) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.29:**
- Maintain info security at an APPROPRIATE LEVEL (graceful degradation)
- Fallback / compensating measures
- Communication paths
- Restoration after disruption ends
- Test schedule

**Loader behaviour:** 0 MUST + 1 SHOULD edge pruned (test_schedule promotion, id preserved). 0 orphan items. All 5 original MUSTs (scenarios / must_continue / fallback / communication / restoration) + 1 original SHOULD (bcp_integration) preserved by id.

**Eval result: 71/72 PASS** run-time. Only #25 known-stale failed; #3 + #21 + #24 all happened to pass — clean run.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~84 thin single-leaf controls remaining (was 85 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 18 controls now
- 17 lifecycle-end variants validated

**Next-likely candidates (still single-leaf):**
- A.5.30 ICT readiness for business continuity (op_process — companion to A.5.29; RTO/RPO + recovery procedures + backup/failover + test records). NATURAL PAIR-BATCH WITH A.5.29.
- A.5.33 protection of records (records_program — pairs with A.5.5/A.5.6/A.5.9 records-family)
- A.5.34 privacy / PII protection (policy_program — extends GDPR-required MUST pattern)
- A.5.36 compliance with policies + standards (op_process or policy_program — meta-control)
