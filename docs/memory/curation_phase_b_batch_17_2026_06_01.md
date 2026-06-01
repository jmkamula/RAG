---
name: curation-phase-b-batch-17-2026-06-01
description: Phase B records_program batch 17 — A.5.33 (Protection of records) promoted to 4-leaf; first records_program promotion since batch 1; SPEC_ART_5_1_E item-id preservation guarded; eval 72/73 → 73/74 clean run
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 17 — single-control records_program promotion. A.5.33
(Protection of records) promoted from the original single-leaf
`records_protection_policy` to a 4-leaf records_program spine pairing
with the batch 1 records-family ([[curation-phase-b-batch-1-2026-05-29]]).

**Why:** Continues [[curation-program-full-multi-leaf]]. A.5.33 is the
natural records-family next step — it's the records-PROTECTION control
and pairs conceptually with A.5.5 (authority register), A.5.6 (SIG
register), A.5.9 (asset register), A.5.31 (legal/regulatory register)
and A.5.32 (IPR inventory). First records_program promotion since
batch 1 — re-validates spine consistency after 11 op_process batches
(3-6, 8-10, 12, 13, 15, 16) + 2 policy_program batches (2, 11) in
between.

**How to apply:** Pattern to reuse for future records_program promotions.
The leaf-id preservation discipline (next bullet) is the key trap.

**Shipped (commit pending — current session 2026-06-01):**
- 4 leaves: records_protection_policy (procedure, preserves prior
  single-leaf id) + records_schedule_register + records_categories_scope
  + records_program_review (freshness=365)
- Eval 72/73 → 73/74 clean run (only #25 known-stale; #24/#3/#21 all
  passed on this run too — third consecutive clean run since batch 15)

**Item-id preservation trap (load-bearing):**
`SPEC_ART_5_1_E` (GDPR Art.5.1.e storage limitation derivation) at
document_requirements.py:6179 references four A.5.33 items by id in
its `scope_items` list:
- `item:A.5.33:records_schedule`
- `item:A.5.33:retention_periods`
- `item:A.5.33:retention_drivers`
- `item:A.5.33:disposal`

ALL FOUR must remain present as ChecklistItem ids somewhere in the
A.5.33 cluster after promotion — if any one is dropped or renamed,
the SPEC_ART_5_1_E DerivedSpec silently loses a leaf. After batch 17,
the first three live on the new register leaf
(`req:A.5.33:records_schedule_register`) and `disposal` lives on the
procedure leaf (`req:A.5.33:records_protection_policy`, where it
belongs — it's a procedure step, not a register row).

Verify after any A.5.33 edit:
```python
needed = ['item:A.5.33:records_schedule', 'item:A.5.33:retention_periods',
         'item:A.5.33:retention_drivers', 'item:A.5.33:disposal']
all_items = [i.id for r in ALL_EVIDENCE_REQUIREMENTS
             if r.control_ref == 'A.5.33'
             for i in (r.must_contain + r.should_contain)]
assert all(n in all_items for n in needed)
```

**Freshness cadence — annual (365d):**
- Records-management methodology is doctrine-level stable (HR records,
  finance records, contracts, audit logs — the schedule itself rarely
  shifts inside a year). Matches A.5.5 (authority contacts, 365d) and
  A.5.6 (SIG memberships, 365d). A.5.31 is the exception at 180d only
  because regulatory change cadence drives it — applicable obligations
  can shift inside the year in ways that authority registers can't.
- A.5.32 IPR audit (365d) is the closest direct sibling cadence — both
  are records-management discipline checks, not detection/IR/identity-
  drift cadences.

**New SHOULD: proc_pii_overlay (ISO × GDPR integration at spec level):**
Encodes that records containing PII inherit GDPR Art.5.1.e storage-
limitation constraints in addition to the ISO 27002 protection
requirements. Third ISO × GDPR integration leaf in Phase B:
1. `pii_overlay` MUST on A.5.13 labelling (batch 10) —
   [[curation-phase-b-batch-10-2026-05-31]]
2. `legal_jurisdiction` MUST on A.5.14 information transfer (batch 11) —
   [[curation-phase-b-batch-11-2026-05-31]]
3. `proc_pii_overlay` SHOULD on A.5.33 (this batch)

The pattern is becoming common — when an ISO control naturally extends
into GDPR territory, encode the integration at spec level rather than
leaving it as cross-control reading. Kept as SHOULD here (not MUST)
because the records-protection policy can be PII-clean (a tax-records-
only org has zero PII to overlay) — unlike A.5.13/A.5.14 where the
GDPR overlap is unavoidable.

**Pairs naturally with batch 1:**
Batch 1 ([[curation-phase-b-batch-1-2026-05-29]]) curated the five
batch-1 records-family controls (A.5.5/A.5.6/A.5.9/A.5.31/A.5.32).
Batch 17 closes the records-protection arc — A.5.33 is the policy
that says "and we protect them" on top of the registers from batch 1.
Cross-control links:
- A.5.33 categories_scope → A.5.31 obligations_scope (same legal/
  regulatory drivers)
- A.5.33 reg_protection_class → A.5.12 classification scheme
- A.5.33 proc_asset_link → A.5.9 asset register
- A.5.33 disposal → A.8.10 information deletion
- A.5.33 proc_pii_overlay → A.5.34 PII protection + GDPR Art.5.1.e

**Live posture flip (Arion):**
Pre-batch: Comply (finding "Relying on MSFT Azure, 365 and RBAC
implementation with document access controls and labeling").
Post-batch: engine proposes NC at 0/4 children satisfied. Reviewer
sees the engine verdict in the Stage-2 surface and can approve/reject.
Surfaces the gap between "we have RBAC" (intake claim) and the actual
records_program shape (no schedule, no categories scope, no program
review).

**Next records-family candidates:**
A.5.34 PII protection (would-be batch 18) is the natural continuation —
single-leaf today, 7 MUST + 2 SHOULD, has freshness_days but no review
discipline. Then A.5.35 independent review and A.5.36 compliance review
round out the A.5.3x policy-and-review block. Three more A.5 controls
to candidate before crossing into A.6/A.7/A.8 spines.
