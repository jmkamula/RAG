---
name: curation-phase-b-batch-8-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.8 single-control batch (project security integration) operational_process 4-leaf; closure_record lifecycle-end variant transfers OWNERSHIP not just artefact (three-way signoff: sponsor + InfoSec + operational owner); review freshness 365d for stable PM methodologies"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Eighth Phase B bulk batch — single-control: A.5.8 (Information security in project management) promoted from single-leaf to operational_process 4-leaf. Continues the program after A.5.1 alignment ([[curation-phase-b-batch-7-2026-05-31]]).

**Spine application (operational_process, procedure-shaped):**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.8 | project_management_security_integration | project_security_register | project_security_program_review **(365d)** | project_security_closure_record |

**Cross-control linkages** (encoded as MUST/SHOULD items):
- register `reg_sdlc_link` (MUST) → A.8.25 / A.8.26 SDLC outputs
- register `reg_supplier_link` (SHOULD) → A.5.20 supplier agreements
- register `reg_cloud_link` (SHOULD) → A.5.23 cloud register
- closure `cls_supplier_handover` (SHOULD) → A.5.22 review duty handover
- closure `cls_lessons_link` (SHOULD) → A.5.27 lessons register

**Why 365d on the program review:** project-management methodologies are structurally stable. Unlike detection/IR landscape (180d batch 4) or threat-intel feeds (180d batch 5), the gate framework + roles + deliverables here change only when the org adopts a new PM methodology or learns a structural lesson. Annual cadence with PMO + InfoSec + Legal jointly is right-sized. Same rationale family as A.5.28 evidence handling (batch 6).

**New lifecycle-end variant locked: closure_record (per-project signoff).** Distinct from prior 10 variants — this is the first lifecycle-end that **transfers OWNERSHIP** not just an artefact. The three-way signoff (sponsor + InfoSec gate-owner + operational owner) is the MUST item that auditors specifically test: residual-risk register transfer must name the operational owner who accepts the risks going forward. Prior variants tracked artefact closure (per-event, per-incident, per-lesson, per-product, per-package); this one tracks who's holding the bag *after* the project team dissolves.

**Engine signature on Arion (post-load):**
- A.5.8 → NC at 0/4 children satisfied (procedure 0/7 + register 0/7 + review 0/7 + closure 0/6)
- Live was Comply (hand-entered finding citing "default integration with ISMS Manager consultation") → engine NC → divergence → status=proposed → Stage-2 surface visible. Standard pattern.

**New MUSTs over the legacy single-leaf:**
- `acceptance_criteria`: risk-acceptance criteria stated; named approver per tier — the missing accountability gate in many "we integrate security" claims
- `change_control`: in-project change control step (scope/security-impact changes during build trigger re-assessment, not late-detection at go-live)

Both were implicit in "integrated into project management" before. They're now load-bearing MUSTs that auditors specifically expect.

**Authority — ISO 27002:2022 § 5.8:**
- Integrate at project initiation, throughout the lifecycle, on closure
- Risk assessment + acceptance per project
- Defined responsibilities (security role with appropriate authority)
- Clear deliverables (gates produce evidence, not just opinions)
- Proportionality (tiering — full vs lightweight vs waived-with-justification)

**Loader behaviour:** 0 stale edges + 0 orphan items pruned. All 5 original MUSTs (initiation_gate / requirements / assessment_pre_golive / role / closure_signoff) and both original SHOULDs (tiering / templates) preserved by id on the new procedure leaf. Pure addition: 2 new MUSTs + 1 new SHOULD on procedure; 7+7+6 MUSTs across the three new sibling leaves.

**Eval result: 63/65 PASS** run-time. Case #25 anti-hallucination known-stale. **Case #3 ("show me our OFI findings") happened to FAIL** via the same LLM citation-stochasticity profile as #21 and #24 — A.5.19 expected in the OFI list, appeared in 5/7 recent runs but missed this one. Re-run of #3 in isolation PASSED. NOT marked as known-stale (~85% reliability across runs; same profile as #21).

**Phase B remaining (post-batch tally):**
- ISO 27001: ~91 thin single-leaf controls remaining (was 92 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 12 controls now (A.5.18 + supplier 4-pack + A.5.23 + incident 3-pack + A.5.7 + A.5.28 + A.5.8)
- 11 lifecycle-end variants validated now: offboarding / deviation / EOL / exit-migration / change-response / triage-decision / incident-closure / improvement-action / per-product / disposal / per-project-closure-signoff
- Spine model unchanged. A.5.8's per-project-closure signoff is the first ownership-transferring variant.

**Stochastic-eval triumvirate now: #3 + #21 + #24.** All three exhibit LLM citation-list-position drift; all three are documented as occasionally-failing-but-not-known-stale because PASS rate is high enough (~70-85%) and re-runs pass. Watch for whether one ratchets down below ~70% PASS rate — that would justify upgrading to known-stale.

**Next-likely candidates (still single-leaf):**
- A.5.11 return of assets (op_process — clean procedure-shaped)
- A.5.13 labelling of information (op_process — could be policy-shaped under classification umbrella)
- A.5.14 information transfer (op_process or policy_program)
- A.5.16 identity management (op_process — touches IAM directly)
