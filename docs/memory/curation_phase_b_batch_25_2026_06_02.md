---
name: curation-phase-b-batch-25-2026-06-02
description: "Phase B batch 25 — ISMS chapters 6 + 7 close-out 10-pack. Planning (6.x) + Support (7.x). New SoA leaf as distinct sibling of 6.1.3 (mandatory under clauses 6.1.3 c-d). Operational/records spine mix replaces batch 24's policy-heavy mix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 25 — chapters 6 + 7 close-out 10-pack. Planning + Support
clauses promoted to 4-leaf Style v2. 30 new evidence requirements
(10 × 4 leaves − 10 primary leaves preserved = 30). Continues the
"three batches by theme" plan started in batch 24: batch 24 = 4 + 5,
batch 25 = 6 + 7 (this one), batch 26 = 8 + 9 + 10.

**Why:** User confirmed "ready" after batch 24 closed chapters 4 + 5.
Chapters 6 + 7 are the natural next group — Planning (risks, objectives,
ISMS changes) and Support (resources, competence, awareness, comms,
documented info).

**How to apply:** Spine mix reflects operational nature of chs 6 + 7
(very different from batch 24's policy-heavy mix):
- 6×op_process: 6.1.1, 6.1.2, 6.1.3, 6.3, 7.3, 7.4 (procedure as primary)
- 3×records_program: 6.2, 7.1, 7.2 (register/record as primary)
- 1×policy_program: 7.5 (doc control policy as primary)

This 6:3:1 spine ratio is the most diverse single-batch mix to date.
Chapters 4 + 5 were direction-setting (policy/scope/directive); chapters
6 + 7 are about ACTUALLY DOING the management system (procedures,
registers, records).

For 6.1.2 and 6.1.3 (anchor REQs at top of file since 2026-05-22), the
primary-leaf ids were preserved across promotion (same pattern as 4.3 +
5.2 in batch 24). All item:6.1.2:* and item:6.1.3:* ids unchanged.

**Shipped (commit pending — current session 2026-06-02):**
- 40 leaves total (10 × 4-leaf = 40), 30 new (10 primary leaves preserved
  on the existing single-leaf REQs)
- 6.1.1 risk + opportunity planning (op_process): planning_procedure +
  action_register + applicable_inputs_scope + program_review (365d).
  Umbrella above 6.1.2/6.1.3. NEW action register tracks ISMS-level
  planning actions distinct from the risk register (6.1.2) and the SoA
  (6.1.3) — covers both risk-addressing AND opportunity-enhancing actions
- 6.1.2 risk assessment (op_process): risk_assessment (primary, id
  preserved) + risk_register + methodology_scope + program_review (365d).
  Risk register is the live output; procedure is the methodology
- 6.1.3 risk treatment (op_process): risk_treatment_plan (primary, id
  preserved) + **statement_of_applicability** (NEW distinct sibling
  leaf) + methodology_scope + program_review (365d). The SoA is the
  first document an external auditor opens on day one — promoted from a
  should_contain item to a distinct mandatory leaf with 7 MUSTs of its
  own. This is the most significant structural change in this batch
- 6.2 security objectives (records_program): objectives_register +
  setting_procedure + applicable_functions_scope + program_review (365d).
  Per-objective owner + KPI + target date + progress status promoted to
  MUSTs (were ad-hoc in original single-leaf)
- 6.3 ISMS change planning (op_process): change_procedure +
  change_register + applicable_change_types_scope + program_review (365d).
  A.8.32 boundary explicitly documented in scope leaf — common audit
  failure: ICT changes mis-routed to 6.3 or ISMS changes mis-routed to
  A.8.32
- 7.1 resources (records_program): resources_record + determination_
  procedure + applicable_categories_scope + program_review (365d).
  Approving-authority MUST added (top management for budget)
- 7.2 competence (records_program): competence_record +
  determination_procedure + applicable_roles_scope + program_review
  (365d). Contractor-coverage SHOULD added (clause 7.2 "persons under
  the org's control" extends to embedded contractors)
- 7.3 awareness (op_process): awareness_programme + completion_register
  + applicable_audience_scope + program_review (365d). ISMS-specific
  awareness explicitly distinct from A.6.3 operational security training
  (cross-link captured for merged-delivery orgs). Completion register
  with per-person expiry/next-due drives refresher triggers
- 7.4 communication (op_process): communication_procedure + event_register
  + applicable_communication_scope + program_review (365d). Event
  register tracks per-comm topic/audience/channel/date/sender. Mandated-
  vs-voluntary split + SLA-met-on-mandated-deadlines as review MUSTs
- 7.5 documented information (policy_program): doc_control_policy +
  document_register + applicable_document_classes_scope + program_review
  (365d). Document register with per-doc next-review date drives stale-
  document detection (single most common audit drift signal). Cross-link
  to A.5.12 classification in register row, A.5.33/A.5.34 retention in
  should_contain
- All 10 engine verdicts: NC 0/4 children satisfied
- All 10 surface in Stage-2 (engine NC ≠ live OFI on every clause)
- 10 eval cases added (140-149), all PASS expected
- 5 MUST + 1 SHOULD edge prunes from old single-leaf state (items
  renamed/moved between new leaves — e.g. 6.2's items_stated + various
  consolidated MUSTs from the old single-leaf rewritten across the new
  4 leaves)

**Item-id preservation:**
NO DerivedSpec references to any chapter 6 / 7 items (confirmed once via
scope_items / direct_evidence grep at batch 24). Primary-leaf ids
preserved for the anchor REQs (req:6.1.2:risk_assessment +
req:6.1.3:risk_treatment_plan) which have been referenced in classifier
patterns since 2026-05-22.

**Posture-seed step (continuing batch-24 pattern):**
All 10 chapter 6+7 clauses had NO posture_controls rows on Arion before
this batch (workbook only covers Annex A). Seeded with finding='OFI'
matching Arion's pre-ISMS narrative:
- 6.1.1: ad-hoc planning informed by exec reviews; no formal procedure
- 6.1.2: threat modelling per major feature; no ISMS-wide risk assessment
- 6.1.3: controls selected case-by-case from cloud-provider catalog; no
  treatment plan or SoA
- 6.2: company OKRs touch security; no dedicated InfoSec objectives
- 6.3: ICT changes via engineering tooling (A.8.32 territory); no separate
  ISMS-level change planning
- 7.1: InfoSec budget allocated annually; no formal resources record
- 7.2: hiring covers required skills; no formal competence record
- 7.3: onboarding includes security; no dedicated ISMS awareness programme
- 7.4: comms ad-hoc Slack + all-hands; no formal procedure or register
- 7.5: docs in shared drive with informal versioning; no policy/register

Batch 26 (chapters 8-10, 8 clauses) will need the same posture-seed step
for 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 10.1, 10.2.

**Spine variant mix (cumulative across ISMS clauses 4-7 = 17 promoted):**
- 6×op_process (6.1.1, 6.1.2, 6.1.3, 6.3, 7.3, 7.4)
- 5×records_program (4.1, 4.2, 6.2, 7.1, 7.2)
- 6×policy_program (4.3, 4.4, 5.1, 5.2, 5.3, 7.5)

Roughly even — reflects that ISMS clauses span the full establishment-
to-operation lifecycle (policy_program for direction-setting, op_process
for procedural execution, records_program for inventory-style records).

**Cross-control link web (compact-style):**
- 6.1.1 → 4.1 (issues input) + 4.2 (requirements input) + 6.1.2 (risk
  assessment link)
- 6.1.2 → 4.1 (issues feed risk identification) + 4.2 (party requirements
  shape risk criteria) + 6.1.3 (treatment plan handoff) + 8.2 (operational
  risk assessment cadence)
- 6.1.3 ↔ 6.1.2 (treatment depends on assessment) + 6.1.3 → Annex A (SoA
  enumerates all 93 controls) + 8.3 (operational treatment execution)
- 6.2 → 5.2 (objectives consistent with policy) + 6.1.2 (objectives
  informed by risk results)
- 6.3 → A.8.32 (boundary) + 4.3 / 4.4 / 5.3 (change records flow up)
- 7.1 → 6.1.3 treatment plan scale + 6.2 objectives + 7.2 / 7.3 competence/
  awareness demand
- 7.2 ↔ 7.3 (competence baseline informs awareness scope)
- 7.3 ↔ A.6.3 (operational security training — possibly merged delivery)
- 7.4 → all communicating clauses (5.2 policy comms, 6.2 objective comms,
  9.1 performance, A.5.26 incident comms, GDPR Art.34 breach
  notification)
- 7.5 → A.5.12 classification + A.5.33 / A.5.34 retention

**Three insights from the planning + support batch:**

1. **SoA deserves its own leaf, not a should_contain item.** The original
   single-leaf REQ_RISK_TREATMENT had `soa_ref` as one MUST item among
   five. Under 6.1.3 c-d the SoA is a MANDATORY artefact with its own
   structural requirements (enumerate all 93 Annex A controls, per-control
   inclusion-status + justification + implementation-status). Promoted to
   a sibling leaf with 7 MUSTs of its own. This pattern should repeat
   anywhere a clause mandates a specific named artefact distinct from the
   primary one (cf. 4.4 process map, 5.2 communication evidence).

2. **The "boundary scope" leaf is doing real work for ISMS clauses.**
   The applicable-X-scope leaves on these 10 promotions explicitly
   document boundaries: 6.3's A.8.32 boundary, 7.2's contractor coverage,
   7.3's "persons under the org's control" interpretation, 7.5's
   ISMS-document-vs-incidental boundary. These edges are where real
   audit findings happen — a clear scope leaf prevents them.

3. **The 6.x cluster has the densest cross-clause web in the standard.**
   6.1.1 → 4.1 + 4.2 + 6.1.2; 6.1.2 → 6.1.3; 6.1.3 → 8.3; 6.2 → 5.2 +
   6.1.2; 6.3 → A.8.32 + 4.3 + 4.4 + 5.3. This is by design — chapter 6
   is the "ISMS becomes operational" stage. Cross-leaf coherence MUSTs in
   the program-review leaves carry this weight.

**Where this leaves the curation arc (post batch 25):**
- ISO 27001 Annex A: closed (93/93 controls multi-leaf)
- ISO 27001 ISMS clauses: 17/25 promoted (4.1, 4.2, 4.3, 4.4, 5.1, 5.2,
  5.3, 6.1.1, 6.1.2, 6.1.3, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5).
  Remaining: 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 10.1, 10.2 = 8 clauses for
  batch 26
- GDPR: untouched. Will be addressed after ISO closes (after batch 26)

**Next batch (batch 26 — final ISO batch):**
Chapters 8 (Operation) + 9 (Performance evaluation) + 10 (Improvement)
— 8 clauses: 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 10.1, 10.2. Anchor REQs for
9.2 and 9.3 exist at top of file (REQ_INTERNAL_AUDIT,
REQ_MANAGEMENT_REVIEW — primary-id preservation pattern same as 4.3/5.2/
6.1.2/6.1.3). Spine prediction: heavy op_process (operational planning,
risk assessment cadence, treatment execution, monitoring, audit
procedure, NC/CA procedure) + records_program (audit programme records)
+ likely review_record-as-primary variant for 9.3 management review
(every review IS the artefact).

See also: [[curation-phase-b-batch-24-2026-06-02]] (chapters 4 + 5 close-
out; posture-seed pattern established), [[curation-phase-b-batch-22-2026-
06-01]] (bulk-batch playbook), [[engine-agreement-suppression]]
(NC==NC suppression rule).
