---
name: curation-phase-b-batch-11-2026-05-31
description: SHIPPED 2026-05-31 — A.5.14 single-control batch (information transfer) policy_program 4-leaf; first policy_program since batch 2 (re-validates spine consistency after 8 op_process batches); new legal_jurisdiction MUST encodes GDPR Chap V Art.44-49 alignment at the spec level
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Eleventh Phase B bulk batch — single-control: A.5.14 (Information transfer) promoted from single-leaf to policy_program 4-leaf. **First policy_program batch since batch 2** ([[curation-phase-b-batch-2-2026-05-30]]) — re-validates spine consistency after eight consecutive operational_process batches (3-10).

**Spine application (policy_program — same shape as A.5.10/A.5.12/A.5.15):**

| Control | Primary leaf | Approval | Communication | Review (freshness) |
|---|---|---|---|---|
| A.5.14 | information_transfer_policy | management_approval | communication_record | periodic_review **(365d)** |

**Why policy_program (not op_process):** ISO 27002:2022 § 5.14 explicitly says the control may be satisfied by "rules, procedures **or** agreements". The org picks the form. Arion's legacy single-leaf was framed as a policy (`evidence_type="policy"`, id ends with `_policy`, live finding cites "we defined policies"). Sticking with policy_program preserves the legacy framing and matches the A.5.10/A.5.12/A.5.15 family pattern.

**Cross-control linkages:**
- policy `scheme_alignment` (MUST) → A.5.12 classification scheme
- policy `legal_jurisdiction` (MUST) → **GDPR Chap V (Art.44-49) — first MUST-level ISO × GDPR integration**
- policy `transfer_agreements` (SHOULD) → A.5.20 supplier agreements

**New MUSTs over the legacy single-leaf:**
- `scheme_alignment`: alignment with A.5.12 stated explicitly. Cascade contract made auditable. Mirrors A.5.13 batch 10 pattern.
- `legal_jurisdiction`: cross-border + GDPR Chap V alignment as a MUST, **not a footnote**. **First batch where GDPR Chapter V international-transfer mechanisms are encoded directly in an ISO 27001 control's MUST citation rationale.** Follows pii_overlay (batch 10) in the ISO × GDPR integration program.

**ISO × GDPR integration progression (tracking across batches):**
- Batch 10 (A.5.13 labelling): `pii_overlay` MUST — "Contains PII" lives ALONGSIDE confidentiality levels
- Batch 11 (A.5.14 transfer): `legal_jurisdiction` MUST — cross-border = GDPR Chap V mechanisms required
- Pattern: where an ISO 27001 control touches PII or transfers, the GDPR alignment is now a MUST, not a SHOULD or footnote

**Engine signature on Arion (post-load):**
- A.5.14 → NC at 0/4 children satisfied (policy 0/7 + approval 0/3 + communication 0/5 + review 0/5)
- Live was Comply (hand-entered "we defined policies and practices" finding citing M365 + SSPA + GDPR) → engine NC → divergence → status=proposed → Stage-2 surface visible.

**Authority — ISO 27002:2022 § 5.14:**
- Rules for all transfer facility types (electronic/physical/verbal)
- Authorisation requirements
- Classification-aware protections
- Jurisdictional + legal considerations (cross-border transfers)
- Transfer agreements with external parties

**Loader behaviour:** 0 stale edges + 0 orphan items. All 6 original MUSTs (electronic_transfer / physical_media / verbal_visual / internal_vs_external / authorisation / legal_jurisdiction) and both original SHOULDs (transfer_agreements / approved_channels) preserved by id on the new policy leaf. Pure addition: 1 new MUST + 1 new SHOULD on policy; 3+5+5 MUSTs on the three new sibling leaves.

**Eval result: 67/68 PASS** run-time. Only #25 known-stale failed; #3, #21, #24 all happened to pass — clean run.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~88 thin single-leaf controls remaining (was 89 pre-batch)
- GDPR: ~297 empty articles still untouched
- policy_program applied to 7 controls now (A.5.1 aligned + A.5.3/4/10/12/15 batch 2 + A.5.14 here)
- operational_process applied to 14 controls
- Spine model unchanged. Family balance: 7 policy_program + 14 op_process + 5 records_program + 4 calibration multi-leaf (Phase A) = 30 multi-leaf controls

**Next-likely candidates (still single-leaf):**
- A.5.16 identity management (op_process — IAM lifecycle)
- A.5.17 authentication information (op_process — credential lifecycle; tightly paired with A.5.16)
- A.5.24 incident management planning (op_process — wraps the A.5.25-27 incident family with strategic planning layer)
- A.5.29 information security during disruption (op_process — BCP-adjacent)
- A.5.30 ICT readiness for business continuity (op_process — same family as A.5.29)
