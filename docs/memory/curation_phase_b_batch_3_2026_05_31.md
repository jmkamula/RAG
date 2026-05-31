---
name: curation-phase-b-batch-3-2026-05-31
description: SHIPPED 2026-05-31 — A.5.19/A.5.20/A.5.21/A.5.22/A.5.23 operational_process 4-leaf supplier+cloud 5-pack; first batch to combine partial-evidence with profile_fact (A.5.23); review freshness varied per spine (180d for A.5.21 ICT volatility)
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

Third Phase B bulk batch — five ISO A.5 supplier + cloud controls promoted from single-leaf to operational_process 4-leaf in one pass. Continues the full multi-leaf curation program ([[curation-program-full-multi-leaf]]) after batch 1 records_program ([[curation-phase-b-batch-1-2026-05-29]]) and batch 2 policy_program ([[curation-phase-b-batch-2-2026-05-31]]).

**Spine application (uniform operational_process, primary-leaf adapted per control):**

| Control | Primary leaf | Register | Review | Lifecycle-end |
|---|---|---|---|---|
| A.5.19 | supplier_risk_procedure | supplier_register | portfolio_review (365d) | offboarding_record |
| A.5.20 | agreement_template | coverage_register | template_review (365d) | deviation_register |
| A.5.21 | ict_supply_chain_procedure | ict_component_register | supply_chain_review **(180d)** | eol_replacement_record |
| A.5.22 | supplier_review_record | review_schedule_register | program_meta_review (365d) | change_response_log |
| A.5.23 | cloud_services_policy | cloud_service_register | cloud_posture_review (365d) | exit_migration_record |

**Engine signatures on Arion (post-load):**
- A.5.19/20/21/22 → NC at 0/4 (no existing evidence on any leaf)
- A.5.23 → **OFI at 1/4** (legacy cloud_services_policy upload carries forward — partial-evidence path)

**Why partial-evidence is interesting:** A.5.23 is the second case (after A.5.15 in batch 2) where existing evidence on the original single-leaf carries through after promotion. It is also the first case combining partial-evidence with `trigger_type=profile_fact` — A.5.23 only fires for cloud-using tenants. Locked by eval case 60.

**Spine variants proven:**
- **Template-as-primary** (A.5.20): an `agreement_template` can occupy the primary slot; lifecycle-end becomes a `deviation_register` (each softened/omitted clause is the supplier "exiting" the standard template path). Mirrors the matrix + directive variants from batch 2 under policy_program.
- **Review-record-as-primary** (A.5.22): a `review_record` can occupy the primary slot; lifecycle-end becomes a `change_response_log` (each supplier-side change is the lifecycle event requiring documented response). The control becomes its own meta-review: the program-meta-review sibling reviews the review-record primary leaf.
- **Policy-as-primary + profile_fact** (A.5.23): `policy` evidence_type works as primary under op_process when the control is fundamentally a topic-specific policy (per ISO 27002 § 5.23 explicit guidance). Profile_fact triggering preserved on all 4 leaves.

**Review freshness — A.5.21 tightened to 180d:** ICT supply chains are volatile — vendor M&A, EOL pipelines, new vulnerability disclosures and sub-supplier shifts can move risk significantly inside a year. 365d cadence is too loose; 180d matches the realistic threat-landscape clock. All other batch 3 review-leaves stay at 365d (procurement portfolio, agreement template, supplier review program, cloud posture all reasonably annual).

**Authority — ISO 27002:2022:**
- § 5.19 items a-n (supplier types, selection, rules, monitoring, training, resilience, transitions, incident handling)
- § 5.20 items a-r (description, classification, legal, obligations, acceptable use, authorized personnel, policies, incident notification, training, sub-processing, contacts, screening, audit rights, defects, independent reports, compliance, termination)
- § 5.21 items a-i (sourcing, propagation, monitoring/validation, critical components, traceability, integrity verification, supply chain visibility, incident sharing, lifecycle)
- § 5.22 items a-k (performance monitoring, reports/meetings, audits, incident exchange, audit trails, problem resolution, sub-supplier oversight, continuity, compliance, corrective actions, change management)
- § 5.23 implementation guidance + cloud-specific agreement clauses

**Loader behaviour:** Pruned 11 MUST + 3 SHOULD stale edges, 14 orphan items — all expected (item ids renamed when single-leaf items moved onto register/review/lifecycle leaves; declarative orphan-pruning from [[loader-orphan-cleanup-followup]] handled the cleanup automatically with no manual intervention).

**Eval result: 54/55 → 58/60 PASS.** Cases 56-60 added (one per promoted control) — 56-59 lock NC 0/4, case 60 locks OFI 1/4 partial-evidence + profile_fact. Case #25 remains the long-running anti-hallucination known-stale (since 2026-05-27); case #24 newly flagged as known-stale (see [[case-24-art32-bridge-followup]] — it had already regressed in batch 2 baseline, not caused by this batch).

**Phase B remaining (post-batch tally):**
- ISO 27001: ~97 thin single-leaf controls remaining (was 102 pre-batch)
- GDPR: ~297 empty articles still untouched
- Pace: 5 controls per session continues to be sustainable
- Spine model unchanged after batch 3 — operational_process applied to 6 controls now (A.5.18 calibration + supplier 4-pack + A.5.23). Three variant adaptations of the lifecycle-end slot validated (offboarding / deviation / change-response / EOL / exit-migration).

**Next-likely candidates:** monitoring/logging-shaped controls (A.5.7 threat intel, A.5.25/26/27 incident triage+response+lessons) — operational_process candidates. Or policy_program siblings still pending (A.5.1 has the master InfoSec policy, A.5.7 threat intel might be policy-shaped).
