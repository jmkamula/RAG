---
name: curation-phase-b-batch-9-2026-05-31
description: SHIPPED 2026-05-31 — A.5.11 single-control batch (return of assets) operational_process 4-leaf; per-leaver return_record lifecycle-end captures BOTH confirmed returns and risk-accepted write-offs; non_return_path MUST surfaces the auditor-critical real-world friction path; review freshness 365d (HR methodology stable)
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Ninth Phase B bulk batch — single-control: A.5.11 (Return of assets) promoted from single-leaf to operational_process 4-leaf. Continues the program after A.5.8 project security ([[curation-phase-b-batch-8-2026-05-31]]).

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.11 | return_of_assets_procedure | leaver_return_register | return_program_review **(365d)** | per_leaver_return_record |

**Cross-control linkages:**
- procedure `data_handling` (MUST) → A.8.10 information deletion
- register `reg_asset_list` (MUST) → A.5.9 asset register
- register `reg_byod_flag` (SHOULD) — drives selective-MDM vs full-wipe
- record `rec_data_attestation` (SHOULD) — BYOD wipe attestation

**Why 365d on the program review:** HR offboarding methodology is structurally stable. The process changes only when the org's workforce model shifts (remote-vs-onsite ratio, contractor mix, BYOD policy). Same rationale family as A.5.8 project security (batch 8), A.5.28 evidence handling (batch 6).

**Per-leaver return_record lifecycle-end variant:** dual-signoff closure with **inclusive write-off path**. Captures BOTH confirmed returns AND documented non-returns with risk-accepted write-off. Every leaver is closed out one way or the other. Aligns with A.5.8's closure_record (batch 8) in tracking "closure with risk transfer" rather than artefact-only closure. **Position 12 in the lifecycle-end variant catalogue**: offboarding / deviation / EOL / exit-migration / change-response / triage-decision / incident-closure / improvement-action / per-product / disposal / per-project-closure-signoff / per-leaver-return.

**New MUSTs over the legacy single-leaf:**
- `data_preservation`: preserve org info BEFORE wipe (not just deletion). Prevents loss of legitimate org records on shared/personal devices.
- `non_return_path`: when assets cannot be physically returned (remote staff / lost device / contractor dispute), alternative attestation + risk acceptance is mandatory. **Auditor-critical**: this is the path that surfaces whether the process actually handles real-world friction or just the easy path.

**Engine signature on Arion (post-load):**
- A.5.11 → NC at 0/4 children satisfied (procedure 0/7 + register 0/7 + review 0/7 + record 0/7)
- Live was Comply (hand-entered BYOD-justified finding) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.11:**
- Return upon termination of employment / change of role / end of contract
- Cover physical + logical assets
- Documentation
- Data preservation prior to return
- Risk-based handling of unreturned items

**Loader behaviour:** 0 stale edges + 0 orphan items. All 5 original MUSTs (triggers / asset_checklist / verification / data_handling / owner) and both original SHOULDs (timeline / exception_process) preserved by id. Pure addition: 2 new MUSTs + 1 new SHOULD on procedure; 7+7+7 MUSTs across the three new sibling leaves.

**Eval result: 64/66 PASS** run-time. #25 known-stale. **#3 LLM-stochastic FAIL** (A.5.19 missing from OFI list) — joins the citation triumvirate (#3 + #21 + #24). Re-runs pass. Not formally known-stale.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~90 thin single-leaf controls remaining (was 91 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 13 controls now (12 before + A.5.11)
- 12 lifecycle-end variants validated

**Next-likely candidates (still single-leaf):**
- A.5.13 labelling of information (op_process — could be policy_program under classification umbrella with A.5.12)
- A.5.14 information transfer (op_process or policy_program)
- A.5.16 identity management (op_process — touches IAM)
- A.5.17 authentication information (op_process — credential lifecycle)
