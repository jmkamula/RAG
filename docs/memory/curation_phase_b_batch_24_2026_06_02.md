---
name: curation-phase-b-batch-24-2026-06-02
description: "Phase B batch 24 — ISMS chapters 4 + 5 close-out 7-pack. First management-system clauses promoted to 4-leaf (4.1/4.2/4.3/4.4/5.1/5.2/5.3). Requires posture-seed step (workbook doesn't import ISMS clauses)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 24 — chapters 4 + 5 close-out 7-pack. First management-system
clauses (vs Annex A controls) promoted to 4-leaf Style v2. 28 new evidence
requirements (7 × 4 leaves). Chosen by user as "three batches by theme" plan:
batch 24 = 4 + 5; batch 25 = 6 + 7; batch 26 = 8 + 9 + 10.

**Why:** User chose "let's continue and close ISO before moving on to GDPR"
after A.8 closed in batch 23. Annex A fully closed (A.5-A.8). The remaining
ISO 27001 surface is clauses 4-10 (25 leaf-level clauses, all single-leaf).
Batch 24 covers context (4.x) + leadership (5.x).

**How to apply:** ISMS clauses are management-system shaped, not operational —
the spine choice reflects this:
- 4.1 / 4.2 = records_program (register-as-primary, like A.5.9/A.5.37)
- 4.3 / 4.4 / 5.1 / 5.2 / 5.3 = policy_program (scope/manual/directive/policy/
  matrix as primary)
- No op_process or technical_control variants — these are establishment-of-ISMS
  clauses, not operational execution.

For 4.3 and 5.2 (which had top-of-file anchor REQs `REQ_ISMS_SCOPE` /
`REQ_ISMS_POLICY` since 2026-05-22), the primary leaf id was preserved across
promotion. The other 5 clauses had bulk-curation single-leaves in the
clauses block at line 9300; those were replaced in-place with 4 leaves each.

**Shipped (commit pending — current session 2026-06-02):**
- 28 leaves total (7 × 4-leaf):
  - 4.1 context (records_program): issues_register + identification_framework +
    applicable_domains_scope + program_review (365d)
  - 4.2 parties (records_program): parties_register + identification_framework +
    applicable_domains_scope + program_review (365d)
  - 4.3 ISMS scope (policy_program): isms_scope + scope_methodology +
    scope_change_record + scope_program_review (365d). PRIMARY ID PRESERVED:
    req:4.3:isms_scope + all item:4.3:* item ids unchanged
  - 4.4 ISMS itself (policy_program): isms_manual + process_map +
    manual_change_record + program_review (365d). Process map is a DISTINCT
    second leaf, not a should_contain item (per the auditor-clarity rule)
  - 5.1 leadership (policy_program): leadership_directive + engagement_framework
    + reaffirmation_record + program_review (365d). Reaffirmation_record is
    the lifecycle-end variant — covers CEO turnover and currency
  - 5.2 InfoSec policy (policy_program): information_security_policy +
    approval_record + communication_evidence + program_review (365d).
    PRIMARY ID PRESERVED: req:5.2:information_security_policy. Communication
    evidence is a DISTINCT leaf — 'approved but not communicated' is a
    common audit finding (deserves its own leaf, not a should_contain)
  - 5.3 ISMS roles (policy_program): roles_matrix + raci_framework +
    roles_change_record + program_review (365d). A.5.2 cross-check baked in
    (5.3 = management-system roles; A.5.2 = operational roles)
- All 7 engine verdicts: NC 0/4 children satisfied
- All 7 surface in Stage-2 (engine NC ≠ live OFI)
- 7 eval cases added (133-139), all PASS expected
- 2 MUST + 6 SHOULD edge prunes from old single-leaf state (items renamed/
  moved between new leaves)

**Item-id preservation:**
NO DerivedSpec references to any clause-4-5 items (confirmed via scope_items /
direct_evidence grep). Item-id preservation was trivial — but I preserved the
primary-leaf ids for 4.3 (req:4.3:isms_scope) and 5.2
(req:5.2:information_security_policy) anyway, since those are the anchors
referenced throughout the codebase (classifier patterns, eval queries).

**Spine variant mix:**
- 2 records_program (register-as-primary, 4.1 + 4.2)
- 5 policy_program (5 different primary types — scope_statement, policy
  (manual), management_directive, policy, responsibility_matrix)

The 2:5 records:policy ratio reflects the management-system shape: chapters
4 and 5 are about CONTEXT (registers — what's around us) and DIRECTION
(policies/directives — what we commit to). Operational execution lives in
chapters 6-10 (which will hit op_process variants in batches 25 + 26).

**Posture-seed NEW STEP for ISMS clauses (key insight):**
Unlike Annex A controls, ISMS clauses are NOT imported by the workbook
(workbook_importer.py only covers A.5-A.8). Posture_controls had no active
rows for 4.1-4.4 on Arion; rows existed for 5.1-5.3 but were inactive
(finding=Comply, deactivated at some prior point).

Without posture rows, the engine doesn't propose anything (see
_persist_engine_proposals in posture_loader.py line 330 — skips on
`cur_row is None`). Stage-2 surface stays empty, eval cases fail.

**Pattern**: when promoting ISMS clauses (chapters 4-10), seed
posture_controls rows BEFORE running eval. Use `finding='OFI'` (or similar
non-NC value) to ensure engine NC ≠ live finding so Stage-2 surfaces. For
Arion (pre-ISMS narrative), OFI is the honest finding — verbal commitment,
informal scope notes, privacy policy in place, CISO appointed; but no
formal ISMS artefacts.

```sql
-- Pattern for clause posture seed (Arion tenant):
INSERT INTO posture_controls (
    tenant_id, standard_id, control_ref, node_id,
    finding, gap_description, source, is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001', 'ISO27001:2022', '<clause>',
    'ISO27001:2022:<clause>', 'OFI', '<honest narrative>', 'assessor', TRUE
);
-- For pre-existing inactive rows: UPDATE ... SET is_active=TRUE, finding='OFI', source='assessor'
```

Batches 25 + 26 will hit the same need for clauses 6.1.1-6.3, 7.1-7.5,
8.1-8.3, 9.1-9.3, 10.1-10.2 (18 more clauses to seed).

**Cross-control link web:**
- 4.1 → 6.1.2 (issues feed risk assessment)
- 4.2 → 4.3 (parties inform scope), 4.2 → 7.4 (communication procedure)
- 4.3 → 4.1 + 4.2 (scope-determination inputs), 4.3 → 6.3 (scope changes
  are ISMS changes)
- 4.4 → 7.4 (manual changes need communication), 4.4 → 6.3 (manual is the
  primary ISMS change-management artefact)
- 5.1 → 9.3 (management review attendance proves leadership), 5.1 → 7.4
  (top-down communication)
- 5.2 → 6.2 (policy frames objectives), 5.2 → 7.3 (policy awareness
  evidence shared with awareness clause)
- 5.3 ↔ A.5.2 (management-system roles vs operational roles — 5.3 is the
  meta-layer above A.5.2)

**Three insights from the first ISMS-clauses batch:**

1. **Spine pattern still works at the management-system layer.** No new
   spine variants needed — records_program + policy_program cover all 7.
   Chapter 6's planning/risk theme might need a new variant (operational
   procedure with cyclical record-keeping) but TBD in batch 25.

2. **Posture-seed step is new and load-bearing.** Workbook intake only
   covers Annex A controls; ISMS clauses need explicit posture rows for the
   engine surface to fire. Documented as a batch-25/26 prerequisite. This
   is a process gap, not a curation gap — the seed could eventually move
   into a migration or a workbook-importer extension.

3. **Cross-leaf coherence MUSTs matter more for ISMS clauses than for
   Annex A.** Annex A controls are mostly self-contained operationally;
   ISMS clauses have rich cross-references (4.1 ↔ 6.1.2 ↔ 8.2,
   5.1 ↔ 5.2 ↔ 5.3, 4.3 ↔ 4.4). Encoded as MUSTs in the program-review
   leaves rather than as standalone leaves.

**Where this leaves the curation arc (post batch 24):**
- ISO 27001 Annex A: closed (93/93 controls multi-leaf, plus A.6.7 as
  profile_fact)
- ISO 27001 ISMS clauses: 7/25 leaf-level clauses promoted (chapters 4 + 5
  done). Remaining: 6.1.1-6.3, 7.1-7.5, 8.1-8.3, 9.1-9.3, 10.1-10.2 = 18
  clauses across batches 25 + 26.
- GDPR: untouched in batch 24. Will be addressed after ISO closes
  (batch 26).

**Next batch (batch 25):**
Chapters 6 (Planning) + 7 (Support) — 10 clauses: 6.1.1, 6.1.2, 6.1.3,
6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5. Anchor REQs for 6.1.2/6.1.3 exist at
top of file (REQ_RISK_ASSESSMENT, REQ_RISK_TREATMENT — primary-leaf id
preservation pattern same as 4.3/5.2 in this batch). Spine prediction:
mix of op_process (procedures — risk planning, change planning,
operational planning) + records_program (resources record, competence
record, objectives register) + policy_program (document-control policy).

See also: [[curation-phase-b-batch-22-2026-06-01]] (bulk-batch playbook),
[[curation-phase-b-batch-23-2026-06-01]] (largest-batch lessons),
[[engine-agreement-suppression]] (NC==NC suppression rule),
[[loader-er-orphan-cleanup-followup]] (orphan-pruning fix that made this
batch's edge prunes harmless).
