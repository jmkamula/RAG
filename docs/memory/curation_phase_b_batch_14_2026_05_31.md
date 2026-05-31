---
name: curation-phase-b-batch-14-2026-05-31
description: SHIPPED 2026-05-31 — A.5.24 single-control batch (incident management planning) operational_process 4-leaf; sits ABOVE the operational incident family (A.5.25-27/28); exercise_record lifecycle-end tracks READINESS DRILLS distinct from real-incident records; third batch with GDPR-required MUSTs
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Fourteenth Phase B bulk batch — single-control: A.5.24 (Information security incident management planning) promoted from single-leaf to operational_process 4-leaf. A.5.24 sits **ABOVE** the operational A.5.25-27 incident family ([[curation-phase-b-batch-4-2026-05-31]]) and A.5.28 evidence handling ([[curation-phase-b-batch-6-2026-05-31]]) — A.5.24 is the strategic planning framework; A.5.25-27/28 operationalise it.

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.24 | incident_management_framework | IR_team_register | framework_program_review **(180d)** | per-exercise framework_exercise_record |

**Cross-control linkages (incident-family wiring made explicit):**
- framework `detection` (MUST) → A.5.25 event triage
- framework `assessment` (MUST) → A.5.25 classification
- framework `evidence` (MUST) → A.5.28 evidence handling
- framework `lessons` (SHOULD) → A.5.27 lessons register
- framework `supplier_path` (SHOULD) → A.5.21 supplier incidents
- exercise `ex_lessons_feed` (SHOULD) → A.5.27 lessons register

**Lifecycle-end variant catalogue → position 16: framework_exercise_record.** Per-tabletop / drill / live-simulation activation proof. **Critically distinct from A.5.26's per-incident_closure_record** — A.5.26 tracks REAL INCIDENTS, A.5.24 tracks READINESS DRILLS. Most orgs' IR programs over-rotate on real incidents and under-test the framework; the separate exercise record forces equal visibility of preparation evidence at audit time. The exercise_record specifically catches the "we have an IR plan but we've never actually run an exercise" failure mode.

**Why 180d on the program review:** IR readiness erodes between exercises and incidents. Same volatility family as A.5.25/A.5.26 (180d, batch 4), A.5.16/A.5.17 identity+credentials (180d, batches 12+13).

**GDPR-required MUSTs — THIRD batch to encode ISO × GDPR at MUST level:**
- Batch 10 A.5.13: `pii_overlay` MUST (SHOULD pattern)
- Batch 11 A.5.14: `legal_jurisdiction` MUST (cross-border transfers)
- Batch 14 A.5.24: `personal_data` + `notification` MUSTs (preserved gdpr_required=True from legacy) + NEW `rev_gdpr_72h_feasibility` MUST (review-level audit that the 72h path actually meets the SLA in practice)

The `rev_gdpr_72h_feasibility` MUST is the most pragmatic GDPR-integration item so far — it forces the periodic review to test the SLA empirically, not just procedurally. Pattern: encode the empirical test of regulatory obligations at the review-record level, not just the procedure level.

**SHOULD-promotion pattern — THIRD consecutive batch:**
- Batch 12 A.5.16: `service_accounts` SHOULD → MUST (preserved id)
- Batch 13 A.5.17: `mfa` SHOULD → MUST (preserved id)
- Batch 14 A.5.24: `tested` SHOULD → `exercise_cadence` MUST (**renamed** + promoted) + dedicated lifecycle-end leaf

Batch 14 is the first SHOULD-promotion that also renames the item id (because `tested` is too vague for a MUST; `exercise_cadence` is precise). Verified no external references to old id before rename.

**New MUSTs over the legacy single-leaf:**
- `exercise_cadence` (was `tested` SHOULD; renamed + promoted)
- `communications` (external comms path with thresholds + named owners; previously implicit in 'response')

**Engine signature on Arion (post-load):**
- A.5.24 → NC at 0/4 children satisfied (framework 0/9 + register 0/7 + review 0/7 + exercise 0/7)
- Live was Comply (hand-entered finding citing GDPR 72hr notification + breach notification processes) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.24 a-g:** roles, detection, assessment, response, evidence, lessons, communications.

**Loader behaviour:** 0 MUST + 1 SHOULD edge pruned (the `tested` SHOULD rename). 1 orphan item pruned (the now-unreferenced `item:A.5.24:tested` ChecklistItem after rename to `exercise_cadence`). All 7 original MUSTs (roles / detection / assessment / response / personal_data / notification / evidence) + 2 original SHOULDs (lessons / contacts) preserved by id.

**Eval result: 70/71 PASS** run-time. Only #25 known-stale failed; #3 + #21 + #24 all happened to pass — clean run.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~85 thin single-leaf controls remaining (was 86 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 17 controls now
- 16 lifecycle-end variants validated

**Lifecycle-end variant catalogue — 16 entries — full list:**
1-13: see [[curation-phase-b-batch-12-2026-05-31]] for entries 1-13
14. identity_revocation_record (A.5.16 — batch 12; per-identity disable with SLA-met flag)
15. credential_revocation_record (A.5.17 — batch 13; per-credential with identity-pair MUST)
16. framework_exercise_record (A.5.24 — batch 14; per-readiness-drill — distinct from real-incident records)

**Next-likely candidates (still single-leaf):**
- A.5.29 information security during disruption (op_process — BCP-adjacent; could pair with A.5.30)
- A.5.30 ICT readiness for business continuity (op_process — same family as A.5.29; ideal pair-batch)
- A.5.33 protection of records (records_program — pairs with A.5.5/A.5.6/A.5.9 records-family from batch 1)
- A.5.34 privacy / PII protection (policy_program — extends the GDPR-required MUST pattern further)
- A.5.36 compliance with policies + standards (op_process or policy_program — meta-control)
