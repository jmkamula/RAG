---
name: curation-phase-b-batch-6-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.28 single-control batch (evidence handling) operational_process 4-leaf; first batch with 365d program-review freshness (forensic discipline doesn't churn); disposal_record lifecycle-end variant closes the chain-of-custody end-to-end alongside A.5.25-27 incident family from batch 4"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Sixth Phase B bulk batch — single-control: A.5.28 (Collection of evidence) promoted from single-leaf to operational_process 4-leaf. Continues full multi-leaf curation program ([[curation-program-full-multi-leaf]]) after batch 5 threat-intel ([[curation-phase-b-batch-5-2026-05-31]]). Closes the incident-evidence triangle alongside A.5.25-27 from batch 4 ([[curation-phase-b-batch-4-2026-05-31]]).

**Spine application (operational_process, uniform — no primary-leaf variant):**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.28 | evidence_collection_procedure | evidence_custody_register | evidence_program_review **(365d)** | evidence_disposal_record |

**Cross-control linkages** (encoded as MUST/SHOULD items, not graph edges):
- procedure `incident_link` (SHOULD) → A.5.26 evidence-collection step
- register `reg_source_incident` (MUST) → A.5.26 incident register
- A.5.26's `evidence_collection` MUST step + `reg_evidence_link` SHOULD + `cls_evidence_archive` SHOULD now all resolve naturally to A.5.28 custody register

**Why 365d on the program review — DIFFERENT from batch 4/5 rationale:** evidence-handling is forensically stable. Legal admissibility rules, retention obligations, chain-of-custody methodology and forensic-practice standards do not churn on a sub-annual cycle. Unlike threat-intel (180d for feed-quality drift) or incident/detection (180d for landscape volatility), evidence handling is a procedural discipline whose primary inputs (jurisdictional law, regulatory guidance, case law) move on multi-year cycles. Annual review with legal/compliance counsel is right-sized.

**New lifecycle-end variant locked: disposal_record.** Distinct from earlier variants in scope: the closure here is the *end* of the chain of custody (not a per-event response or per-product output). Closure types: external_handover (with receipt) / retention_destruction (with witness + final hash) / case_closed_internal. The final-hash MUST is the integrity-at-end mirror of the acquisition_hash on the register — same forensic discipline, opposite ends of the lifecycle.

**Engine signature on Arion (post-load):**
- A.5.28 → NC at 0/4 children satisfied (procedure 0/8 + custody_register 0/8 + program_review 0/7 + disposal_record 0/6)
- Live was Comply (hand-entered Audit Log / Incident Log / Monitoring Log finding) → engine NC → divergence → status=proposed → Stage-2 surface visible. Standard pattern.

**Authority — ISO 27002:2022 § 5.28:**
- Internal procedures: identification → collection → acquisition → preservation lifecycle
- Chain of custody enforcement (who/what/when/where/transfer signatures)
- Integrity verification (hashes at acquisition + re-verified at handover)
- Competent personnel (authorised collectors with appropriate certification)
- Liaison with external authorities (law enforcement, regulators)
- Jurisdictional admissibility considerations
- Storage security (read-only / write-blocked, secure vault, environmental controls)

**Loader behaviour:** 0 MUST + 0 SHOULD edges pruned. 0 orphan items. CLEANEST batch in Phase B to date — all 5 original A.5.28 MUSTs (identification/chain_of_custody/acquisition/preservation/retention) and both original SHOULDs (legal_admissibility/third_party_forensics) preserved by id on the new procedure leaf. The new MUSTs (integrity, competence, liaison) and SHOULD (incident_link) are pure additions per § 5.28 implementation guidance.

**Eval result: 62/64 PASS** run-time. Case #25 anti-hallucination known-stale. **Case #21 happened to FAIL** this run via LLM-stochasticity (citing "9.2" ISO clause at position 8-12 in a 10-12-control list — same shape as #24 stochasticity). Re-run of #21 in isolation PASSED. NOT marked as known-stale (PASS×4/FAIL×1 across recent runs). Baseline target ratchets to 60/64 with #24 + #25 as known-stale; #21 documented as occasional LLM-stochastic case alongside #24.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~92 thin single-leaf controls remaining (was 93 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 11 controls now (A.5.18 calibration + supplier 4-pack + A.5.23 + incident 3-pack + A.5.7 + A.5.28)
- Spine model unchanged. A.5.28 validates disposal_record as a fifth lifecycle-end variant (after offboarding/deviation/EOL/exit-migration/change-response/triage-decision/incident-closure/improvement-action/per-product-record).
- First batch with **365d** program review freshness in the operational_process spine — establishes precedent that op_process review freshness should match the *underlying domain's actual change tempo*, not a one-size-fits-all 180d.

**Next-likely candidates:**
- A.5.1 master InfoSec policy (policy_program — still pending after batch 2)
- A.5.8 project security integration (procedure-shaped; op_process)
- A.5.11 return of assets (procedure-shaped; op_process)
- A.5.14 information transfer (could be op_process or policy_program)
