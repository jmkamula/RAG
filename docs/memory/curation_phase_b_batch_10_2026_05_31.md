---
name: curation-phase-b-batch-10-2026-05-31
description: SHIPPED 2026-05-31 — A.5.13 single-control batch (information labelling) operational_process 4-leaf; cascade pair with A.5.12 classification (parent scheme); per-platform application_record lifecycle-end variant; new pii_overlay MUST pins ISO confidentiality × GDPR PII integration
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Tenth Phase B bulk batch — single-control: A.5.13 (Labelling of information) promoted from single-leaf to operational_process 4-leaf. Cascade pair with A.5.12 classification (already 4-leaf policy_program from batch 2 — [[curation-phase-b-batch-2-2026-05-30]]). The scheme lives in A.5.12; application of the scheme lives in A.5.13.

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.13 | information_labelling_procedure | labelling_coverage_register | labelling_program_review **(365d)** | labelling_application_record |

**Cross-control linkages:**
- procedure `physical_media` (MUST) → A.7.10 storage media
- procedure `scheme_alignment` (MUST) → A.5.12 classification scheme
- procedure `training_ref` (MUST) → A.5.12 training material
- register `reg_classification_levels` (MUST) → A.5.12 levels deployed
- register `reg_dlp_policy` (SHOULD) — DLP enforcement of labels
- record `app_dlp_wired` (SHOULD) — DLP rule wired per platform

**Why 365d on the program review (cascade rationale):** labelling cascades from the A.5.12 classification scheme. Reviewing labelling out of sync with the scheme produces misaligned controls — the level taxonomy must match. Same rationale family as A.5.8 / A.5.11 / A.5.28 (stable underlying methodology); locked to parent cadence. First batch that establishes the **cascade-cadence pattern**: where a control's effective interval is constrained by a *parent* control's cycle, not by its own domain volatility.

**Per-platform application_record lifecycle-end variant:** position 13 in the catalogue. Joins the "estate growth requires program extension" shape — proves labelling was actually extended to each new platform onboarded, not just retained on the legacy set. Distinct semantics from A.5.8 closure_record (project ownership transfer) and A.5.11 return_record (per-leaver completion); A.5.13 application_record is **per-system coverage-extension proof**.

**New MUSTs over the legacy single-leaf:**
- `scheme_alignment`: alignment with A.5.12 scheme stated explicitly (level names + count + semantics match). The cascade contract made auditable.
- `pii_overlay`: PII/personal-data overlay rule. Codifies the practical fact that "Contains PII" lives ALONGSIDE confidentiality levels (not within them) for GDPR alignment. This is the first MUST in any batch that explicitly pins **ISO 27001 confidentiality × GDPR PII** integration at the spec level — Arion's "Contains PII footer regardless of classification level" pattern is now standard-codified, not just a tenant practice.

**Engine signature on Arion (post-load):**
- A.5.13 → NC at 0/4 children satisfied (procedure 0/7 + register 0/7 + review 0/7 + record 0/7)
- Live was Comply (hand-entered Purview-based finding) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.13:**
- Procedures covering digital and physical labelling
- Level-appropriate marking
- Persistence across transformations
- Training
- Legacy-handling rules

**Loader behaviour:** 0 stale edges + 0 orphan items. All 5 original MUSTs (visual_marks / metadata_tags / physical_media / label_persistence / training_ref) and both original SHOULDs (legacy_handling / automation) preserved by id. Pure addition: 2 new MUSTs + 1 new SHOULD on procedure; 7+7+7 MUSTs across the three sibling leaves.

**Eval result: 65/67 PASS** run-time. Cases #24 + #25 BOTH known-stale this run (#24 within its ~30-50% pass rate). Cases #3 + #21 happened to pass. Case 67 (A.5.13) PASS.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~89 thin single-leaf controls remaining (was 90 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 14 controls now
- 13 lifecycle-end variants validated
- Cascade-cadence pattern (review freshness inherited from parent) — first invocation here; documented for reuse

**Next-likely candidates (still single-leaf):**
- A.5.14 information transfer (op_process or policy_program — transfers cross both organisational + cross-org boundaries; could be either spine)
- A.5.16 identity management (op_process — IAM lifecycle)
- A.5.17 authentication information (op_process — credential lifecycle)
- A.5.24 incident management planning (op_process — paired with A.5.25-27 incident family from batch 4)
