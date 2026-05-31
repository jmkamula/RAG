---
name: curation-phase-b-batch-12-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.16 single-control batch (identity management) operational_process 4-leaf; revocation_record with SLA-met flag is auditor-critical (proves the famous '24h of last day' timeliness promise); service_accounts promoted SHOULD→MUST; review freshness 180d (high-volume identity drift)"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Twelfth Phase B bulk batch — single-control: A.5.16 (Identity management) promoted from single-leaf to operational_process 4-leaf. Continues the program after A.5.14 information-transfer ([[curation-phase-b-batch-11-2026-05-31]]).

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.16 | identity_management_procedure | identity_register | identity_program_review **(180d)** | per-identity revocation_record |

**Cross-control linkages:**
- procedure `ownership` (MUST) → A.5.11 leaver register cascade
- procedure `authn_link` (MUST) → A.5.17 authentication info (paired credential lifecycle)
- procedure `attestation` (SHOULD) → A.5.18 access rights review
- register `reg_hr_link` (MUST) → HR system + A.5.11 cascade
- record `rev_credential_link` (SHOULD) → A.5.17 credential revocation

**Why 180d on the program review:** identity drift is high-volume. Joiners, leavers, role changes, contractor onboarding/offboarding, service-account churn all accumulate continuously. Same volatility family as A.5.25/A.5.26 detection landscape (180d, batch 4) and A.5.21 ICT supply chain (180d). Distinct from the stable-methodology family (A.5.8/A.5.11/A.5.28 at 365d) — even though A.5.11 also deals with offboarding, A.5.11's *methodology* doesn't change much, whereas A.5.16's *state* changes every business day.

**Revocation_record lifecycle-end variant (position 14 in catalogue):** per-identity disable proof with **SLA-met flag**. This is the auditor-critical promise made first-class — proves not just THAT each identity was disabled but that the disable timestamp was within the stated SLA. The famous "X was disabled within 24h of last day" claim becomes an audit-defensible per-record fact rather than a procedural aspiration.

**Key MUST promotion: service_accounts (SHOULD → MUST).** Service / shared / non-human account governance is the weakest spot in most orgs' identity hygiene. Promoting it to MUST elevates it to first-class. Companion register MUST `reg_service_expiry` forces deliberate renewal rather than indefinite drift. Together these encode "every non-human identity has a named human owner and a deadline" as the audit-default.

**New MUSTs over the legacy single-leaf:**
- `service_accounts` (promoted from SHOULD; named human owner, expiry, scope, monitoring)
- `authn_link` (cross-reference to A.5.17; credential issuance and revocation are PAIRED with identity events, not separate processes — closes the famous gap where identity gets disabled but creds linger)

**Engine signature on Arion (post-load):**
- A.5.16 → NC at 0/4 children satisfied (procedure 0/8 + register 0/8 + review 0/7 + revocation 0/7)
- Live was Comply (empty gap_description) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.16:**
- Full identity lifecycle management (creation / modification / suspension / termination)
- Timeliness expectations
- Accountability per phase (HR triggers, IT executes, manager approves)
- Unique identity per person
- Service-account governance
- Periodic attestation

**Loader behaviour:** 0 MUST + 1 SHOULD edge pruned. The 1 SHOULD prune is the old `item:A.5.16:service_accounts` SHOULD — now MUST per above. All 6 original MUSTs (creation / modification / suspension / termination / unique_identity / ownership) and the 1 remaining original SHOULD (attestation) preserved by id.

**Eval result: 68/69 PASS** run-time. Only #25 known-stale failed; #3, #21, #24 all happened to pass — **second consecutive clean run** (batch 11 also was 67/68 with only #25 failing).

**Phase B remaining (post-batch tally):**
- ISO 27001: ~87 thin single-leaf controls remaining (was 88 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 15 controls now
- 14 lifecycle-end variants validated

**Lifecycle-end variant catalogue (14 entries) — full list:**
1. offboarding_record (A.5.19 — batch 3)
2. deviation_register (A.5.20 — batch 3)
3. eol_replacement_record (A.5.21 — batch 3)
4. exit_migration_record (A.5.23 — batch 3)
5. change_response_log (A.5.22 — batch 3)
6. triage_decision_record (A.5.25 — batch 4)
7. incident_closure_record (A.5.26 — batch 4)
8. improvement_action_record (A.5.27 — batch 4)
9. intel_product_record (A.5.7 — batch 5; per-product output)
10. evidence_disposal_record (A.5.28 — batch 6; chain-of-custody end)
11. project_security_closure_record (A.5.8 — batch 8; per-project signoff with ownership transfer)
12. per_leaver_return_record (A.5.11 — batch 9; per-leaver completion + write-off)
13. labelling_application_record (A.5.13 — batch 10; per-platform enablement)
14. identity_revocation_record (A.5.16 — batch 12; per-identity disable with **SLA-met flag**)

**Next-likely candidates (still single-leaf):**
- A.5.17 authentication information (op_process — naturally paired with A.5.16; credential lifecycle alongside identity lifecycle)
- A.5.24 incident management planning (op_process — wraps A.5.25-27 incident family with strategic planning layer)
- A.5.29 information security during disruption (op_process — BCP-adjacent)
- A.5.30 ICT readiness for business continuity (op_process — same family as A.5.29)
