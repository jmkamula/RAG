---
name: curation-phase-b-batch-13-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.17 single-control batch (authentication info) operational_process 4-leaf, naturally PAIRED with A.5.16 from batch 12. MFA promoted SHOULD→MUST (modern baseline). New rev_identity_pair MUST enforces the A.5.16 ↔ A.5.17 lifecycle pairing"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Thirteenth Phase B bulk batch — single-control: A.5.17 (Authentication information) promoted from single-leaf to operational_process 4-leaf. **Naturally PAIRED with A.5.16** ([[curation-phase-b-batch-12-2026-05-31]]). A.5.16 governs the identity *object*, A.5.17 governs how each identity *proves* itself (credentials, factors, tokens).

**Spine application:**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.17 | authentication_information_procedure | credential_register | authentication_program_review **(180d)** | per-credential revocation_record |

**The A.5.16 ↔ A.5.17 pairing made enforceable:**
- A.5.17 procedure `identity_link` (MUST) → A.5.16 identity lifecycle
- A.5.17 register `reg_identity_link` (MUST) → A.5.16 register
- A.5.17 record `rev_identity_pair` (MUST) → paired A.5.16 revocation record
- A.5.16 procedure `authn_link` (MUST, from batch 12) → A.5.17 credential lifecycle
- A.5.16 record `rev_credential_link` (SHOULD, from batch 12) → A.5.17 credential revocation

The pairing is now bidirectionally encoded. Auditors can verify: when an identity is revoked, the corresponding credentials are revoked too (closes the famous "identity disabled but creds linger" gap).

**Why 180d on the program review:** credential hygiene churns continuously (rotation cycles, breach disclosures triggering forced rotations, MFA enrolment campaigns, factor-class additions/deprecations). Same volatility family as A.5.16 (180d, batch 12) and A.5.25/A.5.26 detection landscape.

**Lifecycle-end variant catalogue → position 15:** per-credential revocation_record with `rev_identity_pair` MUST. Distinct from A.5.16's per-identity revocation_record (position 14) — credentials have independent lifecycles (rotation, lost-token reissue, factor downgrade) that don't change the identity itself.

**Key MUST promotion: MFA (SHOULD → MUST).** Same pattern as service_accounts in batch 12. Phishable single-factor auth is no longer acceptable baseline. The promotion makes "MFA mandated for in-scope access (admin, remote, sensitive data)" an audit-default rather than aspirational guidance.

**New MUSTs over the legacy single-leaf:**
- `mfa` (promoted from SHOULD; mandated for in-scope access)
- `identity_link` (cross-reference to A.5.16; pairing enforced)
- `compromise_response` (compromise-response path mandated — forced rotation, identity-level investigation, scope expansion check)

**SHOULD-promotion pattern (now observed twice — batches 12 + 13):**
- batch 12 A.5.16: `service_accounts` SHOULD → MUST (weakest spot in identity hygiene)
- batch 13 A.5.17: `mfa` SHOULD → MUST (modern baseline; phishable auth not acceptable)

Pattern: **first-class promotion of previously-soft expectations that have become security baselines.** Other controls may have similar candidates (e.g. A.8.5 MFA in technical-controls space; A.5.31 legal/regulatory compliance recurrence).

**Engine signature on Arion (post-load):**
- A.5.17 → NC at 0/4 children satisfied (procedure 0/9 + register 0/7 + review 0/7 + revocation 0/7)
- Live was Comply (empty gap_description) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.17:**
- Allocation of authentication info
- Management (transmission/storage/complexity/rotation)
- Reset/recovery process
- Personnel responsibilities (handling, reporting compromise)
- MFA where appropriate

**Loader behaviour:** 0 MUST + 1 SHOULD edge pruned (the `mfa` promotion). All 6 original MUSTs (allocation / transmission / complexity / storage / reset / user_advisory) and 1 original SHOULD (factor_classes) preserved by id.

**Eval result: 68/70 PASS** run-time. Both #24 + #25 known-stale failed (#24 within ~30-50% pass rate); #3 + #21 happened to pass.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~86 thin single-leaf controls remaining (was 87 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 16 controls now
- 15 lifecycle-end variants validated

**Next-likely candidates (still single-leaf):**
- A.5.24 incident management planning (op_process — wraps A.5.25-27 incident family from batch 4 with strategic planning layer)
- A.5.29 information security during disruption (op_process — BCP-adjacent)
- A.5.30 ICT readiness for business continuity (op_process — same family as A.5.29; could be pair-batch with A.5.29)
- A.5.33 protection of records (records_program — pairs with A.5.5/A.5.6/A.5.9 records-family from batch 1)
- A.5.34 privacy/PII protection (policy_program — extends the GDPR-integration MUST pattern from batches 10/11)
