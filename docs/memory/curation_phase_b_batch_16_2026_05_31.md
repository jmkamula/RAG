---
name: curation-phase-b-batch-16-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.30 single-control batch (ICT readiness) operational_process 4-leaf, natural pair with A.5.29 from batch 15. Second HYBRID lifecycle-end variant (position 18). Freshness-convention cleanup — removed freshness_days from plan leaf, moved to review only. rec_success_status MUST is the RTO-met auditor-critical proof"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Sixteenth Phase B bulk batch — single-control: A.5.30 (ICT readiness for business continuity) promoted from single-leaf to operational_process 4-leaf with **plan-as-primary** variant. **NATURAL PAIR** with A.5.29 ([[curation-phase-b-batch-15-2026-05-31]]).

**A.5.29 ↔ A.5.30 pairing — fully wired:**
- A.5.29 = security-annex layer (which controls hold during disruption)
- A.5.30 = mechanical ICT recovery layer (what infrastructure recovers, in what order)
- A.5.30 plan `bcp_alignment` MUST → A.5.29 plan
- A.5.29 plan `restoration` MUST → A.5.30 ICT readiness
- A.5.30 record `rec_disruption_link` SHOULD → A.5.29 activation_record
- A.5.30 review `rev_scenario_coverage` MUST → A.5.29 scenario register

Together the two controls define the org's complete continuity stance. The pairing is now bidirectionally encoded — auditors testing one will be guided to the other via MUST/SHOULD cross-links.

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.30 | ict_continuity_plan **(plan)** | ict_service_register | ict_program_review **(180d)** | per-recovery HYBRID record |

**Second HYBRID lifecycle-end variant (position 18 in catalogue) — pattern reproduces:** A.5.30's recovery_record uses the same hybrid pattern as A.5.29's activation_record (introduced batch 15). Both cover real events AND scheduled tests via a type field. The HYBRID pattern is now **validated as reusable for paired BCP controls** — likely applicable to any future control where the artefact activates identically regardless of trigger source.

**Auditor-critical MUST: `rec_success_status`.** Captures rto_met / rto_missed_with_reason / partial_recovery_acceptable / failed. Analogous to A.5.16's `rev_sla_met` flag (batch 12) — proves not just THAT recovery happened but that **RTO commitments were ACTUALLY met**. Pattern: where a control has an explicit quantitative commitment (24h SLA, RTO target, 72h notification), the lifecycle-end record needs an explicit-met-flag MUST.

**New MUSTs over the legacy single-leaf:**
- `bia_link`: RTO/RPO targets must trace to the BIA — not arbitrary numbers. Pins the "where did these targets come from?" auditor question.
- `bcp_alignment`: mechanical recovery layer + A.5.29 security-annex layer must reconcile. Pins the pair-control coherence at the spec level.

**No SHOULD-promotions this batch — breaks the 4-batch streak (batches 12-15).** A.5.30's legacy SHOULDs (`scenario_coverage`, `communication_tree`) are both genuine SHOULDs — neither is the "load-bearing soft expectation" that warranted promotion in prior batches. Pattern: SHOULD-promotion is appropriate when the legacy SHOULD is structurally critical; not appropriate when the SHOULD is genuinely supplementary.

**Freshness-convention cleanup — first in Phase B:**
- Legacy A.5.30 had `freshness_days=365` on the plan leaf
- Removed; moved to review_record only (`freshness_days=180`)
- Matches the convention across A.5.7 / A.5.8 / A.5.11 / A.5.13 / A.5.16 / A.5.17 / A.5.24 / A.5.28 / A.5.29 — the rest of the op_process spine has freshness ONLY on review
- Behavioural impact on Arion: nil (only hand-entered Comply finding; no uploaded plan evidence)

**Why this cleanup matters:** plan/procedure-leaf freshness conflated two concepts ("the plan must exist" vs "the plan must be reviewed periodically"). Separating them onto plan + review_record means the engine can flag specifically WHICH aspect is stale — was the plan never produced, or just not reviewed? Better diagnostic surface.

**Engine signature on Arion (post-load):**
- A.5.30 → NC at 0/4 children satisfied (plan 0/7 + register 0/7 + review 0/7 + record 0/8)
- Live was Comply (hand-entered finding citing Azure + M365 redundancy + quarterly tabletops) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.30:** planned, implemented, maintained, tested; BIA-derived RTO/RPO; recovery procedures; backup + failover; test records.

**Loader behaviour:** 0 stale edges + 0 orphan items. Pure addition — all 5 original MUSTs (rto_rpo / recovery_procedures / backup / failover / test_records) + 2 original SHOULDs (scenario_coverage / communication_tree) preserved by id. 2 new MUSTs + 1 new SHOULD on plan; 7+7+8 MUSTs across the three new sibling leaves.

**Eval result: 72/73 PASS** run-time. Only #25 known-stale failed. **Third consecutive clean run** (batches 14, 15, 16 all had only #25 known-stale fail).

**Phase B remaining (post-batch tally):**
- ISO 27001: ~83 thin single-leaf controls remaining (was 84 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 19 controls now
- 18 lifecycle-end variants validated
- Both BCP-adjacent controls (A.5.29 + A.5.30) now covered

**BCP-adjacent control coverage map:**
- A.5.24 incident planning (batch 14) — strategic IR framework
- A.5.29 disruption security (batch 15) — security-annex during disruption
- A.5.30 ICT readiness (batch 16) — mechanical ICT recovery
- A.5.25-27 incident family (batch 4) — operational incident handling
- A.5.28 evidence handling (batch 6) — forensic discipline

Five controls now define the full incident → disruption → recovery → lessons loop. The cross-linkage MUST/SHOULD pattern across these controls is dense — testing one surfaces the others via auto-derivation.

**Next-likely candidates (still single-leaf):**
- A.5.33 protection of records (records_program — pairs with A.5.5/A.5.6/A.5.9 records-family from batch 1)
- A.5.34 privacy / PII protection (policy_program — extends GDPR-required MUST pattern from batches 10/11/14)
- A.5.36 compliance with policies + standards (op_process or policy_program — meta-control)
- A.5.37 documented operating procedures (op_process — meta-procedure-control)
