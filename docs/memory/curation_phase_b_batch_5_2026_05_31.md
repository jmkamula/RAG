---
name: curation-phase-b-batch-5-2026-05-31
description: SHIPPED 2026-05-31 — A.5.7 single-control batch (threat intelligence) operational_process 4-leaf; review freshness 180d for same detection-landscape-volatility rationale as batch 4 incident family; first single-control Phase B batch
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Fifth Phase B bulk batch — single-control: A.5.7 (threat intelligence) promoted from single-leaf to operational_process 4-leaf. First Phase B batch sized at a single control rather than a 3–5-pack. Continues full multi-leaf curation program ([[curation-program-full-multi-leaf]]) after batch 4 incident family ([[curation-phase-b-batch-4-2026-05-31]]).

**Spine application (operational_process, uniform — no primary-leaf variant):**

| Control | Primary leaf | Register | Review (freshness) | Lifecycle-end |
|---|---|---|---|---|
| A.5.7 | threat_intelligence_procedure | threat_intel_feed_register | threat_intel_program_review **(180d)** | intel_product_record |

**Cross-control linkages** (encoded as MUST items, not graph edges):
- feed_register `reg_internal_input` ← A.5.6 SIG-membership outputs + internal IR observations
- program_review `rev_consumer_feedback` → A.5.21 supplier risk, A.5.25 detection, exec briefing
- program_review `rev_missed` ↔ A.5.25 + A.5.27 (events that triage missed / lessons that intel didn't flag in advance)

**Why 180d on the program review:** detection landscape volatility (feed quality shifts, IOC libraries age within weeks, new TTPs emerge inside a quarter) outpaces annual cadence. Same rationale as A.5.25 + A.5.26 in batch 4. Feed register itself has no freshness (registers are continuous; per the convention established in batches 3+4).

**Lifecycle-end variant locked: per-product record.** A.5.27 uses improvement_action_record (per-lesson action), A.5.25 uses triage_decision_record (per-event decision), A.5.26 uses incident_closure_record (per-incident closure). A.5.7 adds the **per-deliverable artefact** shape: each published intelligence product (IOC list / advisory / briefing) tied to named consumer and downstream action taken (firewall rule / IDS signature / risk register update / no-op). This is a new variant: the "lifecycle-end" is *the program's output itself*, not an event the program closes.

**Engine signature on Arion (post-load):**
- A.5.7 → NC at 0/4 children satisfied (procedure 0/8 + feed_register 0/7 + program_review 0/7 + intel_product_record 0/6)
- Live was Comply (hand-entered PIMS-tagged finding) → engine NC → divergence → status=proposed → Stage-2 surface visible. Standard pattern, no [[engine-agreement-suppression]] concern.

**Authority — ISO 27002:2022 § 5.7:**
- Three intelligence layers: strategic (sector/long-term), tactical (attacker methodologies/TTPs), operational (specific attack details/IOCs)
- Activities: sources establishment, collection, analysis (relevance, integrity, completeness), communication, sharing of analysed intelligence
- Use into: technical controls (firewall rules, IDS signatures, EDR indicators), vulnerability prioritisation, exercise planning, risk treatment

**Loader behaviour:** 0 MUST + 1 SHOULD edge pruned (old `item:A.5.7:risk_feedback` SHOULD → now MUST on procedure leaf per § 5.7 "informed risk treatment"); 0 orphan items. Clean — declarative pruning handled the rename automatically.

**Eval result: 60/62 → 62/63 PASS** in actual run (run shows #24 happened to pass; baseline target remains 60/63 with #24 + #25 known-stale per [[case-24-art32-bridge-followup]]). Case 63 added — exercises Stage-2 list_one surface, asserts "0/4 children satisfied" reason text.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~93 thin single-leaf controls remaining (was 94 pre-batch)
- GDPR: ~297 empty articles still untouched
- operational_process applied to 10 controls now (A.5.18 calibration + supplier 4-pack + A.5.23 + incident 3-pack + A.5.7)
- Spine model unchanged. A.5.7 validates per-product-record as a fourth lifecycle-end variant (after offboarding/deviation/EOL/exit-migration/change-response/triage-decision/incident-closure/improvement-action).

**Next-likely candidates:**
- A.5.28 evidence handling (single-leaf, procedure-shaped, op_process; would close the incident-evidence triangle alongside A.5.25-27)
- A.5.1 master InfoSec policy (policy_program — still pending after batch 2)
- A.5.8 project security integration (procedure-shaped; would extend op_process spine)
