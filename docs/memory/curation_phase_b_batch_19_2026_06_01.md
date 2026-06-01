---
name: curation-phase-b-batch-19-2026-06-01
description: Phase B A.5.3x close-out 3-pack — A.5.35/A.5.36/A.5.37 all promoted to 4-leaf records_program; first multi-control batch since batch 4; closes the A.5 organisational controls arc; eval 75/76 → 78/78 clean upper bound
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 19 — three-control records_program promotion. A.5.35
(Independent review) + A.5.36 (Compliance review records) + A.5.37
(Documented operating procedures) all promoted from single-leaf to
4-leaf, closing out the A.5.3x review/procedure block.

**Why:** Continues [[curation-program-full-multi-leaf]]. User
requested bundled batches now that the pattern is locked in
([[curation-phase-b-batch-17-2026-06-01]] +
[[curation-phase-b-batch-18-2026-06-01]] proved single-control
batches are smooth). Closes the A.5 organisational-controls arc
that started with case #46 (batch 1 records-family). The full A.5
block (except A.5.18 Access rights, which started the whole arc
via case #1) is now multi-leaf.

**How to apply:** Multi-control batching is the new default for any
batch where the controls share a spine variant + similar evidence
shape. Use [[curation-phase-b-batch-3-2026-05-31]] (supplier+cloud
5-pack) and [[curation-phase-b-batch-4-2026-05-31]] (incident triage
3-pack) as precedents — same pattern, more familiar territory now.

**Shipped (commit pending — current session 2026-06-01):**
- 12 leaves total (3 × 4-leaf), all records_program spine variants:
  - **A.5.35** review-record-as-primary (same shape as A.5.22):
    independent_review_report (preserves id; freshness=365) +
    review_schedule_register + review_program_meta_review +
    finding_response_register (lifecycle-end)
  - **A.5.36** review-record-as-primary (batch-mate of A.5.35):
    compliance_review_record (preserves id; freshness=365) +
    compliance_review_schedule + compliance_program_meta_review +
    nonconformity_register (lifecycle-end)
  - **A.5.37** register-as-primary (same shape as A.5.9 asset
    register): operating_procedures_register (preserves id) +
    procedures_maintenance_procedure + applicable_facilities_scope
    + procedures_program_review (freshness=365)
- All three engine verdicts: NC at 0/4 children satisfied. Live
  postures (all Comply pre-batch with various hand-entered findings)
  flip to engine-proposed NC in Stage-2.
- Eval 75/76 → 78/78 clean upper bound (cases 76/77/78 PASS on
  first run; #21 stochastic FAIL + #25 known-stale FAIL).

**Item-id preservation:**
None of the three controls have any DerivedSpec references to their
item ids. Only the existing primary-leaf ids need preservation,
which is the default `preserves_id` discipline. Easy batch on
preservation grounds — unlike A.5.34 with TWO DerivedSpecs.

**Three variants in one batch (validates the spine):**
- **review-record-as-primary** (A.5.22 / A.5.35 / A.5.36) — when
  the control's primary artefact is a per-cycle review record.
  Sibling shape: schedule_register + program_meta_review + lifecycle-
  end register (change_response_log / finding_response_register /
  nonconformity_register).
- **register-as-primary** (A.5.5 / A.5.6 / A.5.9 / A.5.31 / A.5.32 /
  A.5.37) — when the control's primary artefact is an operational
  register. Sibling shape: maintenance_procedure + scope + review.
- **procedure-as-primary** (A.5.33 / A.5.34 / many op_process) —
  when the control's primary artefact is a policy or procedure.
  Sibling shape: register + scope + review.

The records_program spine ratified across all three variants now,
with multiple precedents per variant. Future curation can confidently
pick variant by primary-artefact shape.

**New MUSTs encoding rubber-stamping failure modes:**
Three new MUSTs across this batch encode the "we said we did it
but didn't really" failure mode — the audit-defensibility gap that
single-leaf curation misses:
- A.5.35 `pgm_independence_check` — meta-review audits whether
  actual reviewers met the independence criteria (rotation worked?
  reviewer reviewing their own area?)
- A.5.36 `pgm_method_review` — meta-review audits whether the
  chosen review methods are surfacing real NCs or have become
  rubber-stamps
- A.5.37 `rev_accuracy_sample` — reviewer must walk through a
  sample procedure end-to-end (not just "list says yes")
- A.5.37 `rev_emergency_review` — emergency-use procedures (DR, IR)
  get an extra review pass because stale = catastrophic

These four MUSTs collectively encode "program health vs program
existence" — the difference between "we have a process" and "the
process is actually working".

**Cross-control links established this batch:**
- **A.5.35 ↔ A.5.36 finding registers**: bidirectional SHOULD link
  (fr_cross_review_link / nc_cross_review_link) — mature programs
  often keep one finding register that serves both
- **A.5.36 → A.5.35 program alignment**: pgm_a535_alignment SHOULD
  — shared reviewer pool, infrastructure leverage
- **A.5.37 → A.5.9 asset register**: scope_asset_link MUST —
  every information asset that is a facility should map to one or
  more procedures
- **A.5.37 → A.5.24/A.5.26/A.5.29/A.5.30**: related_controls_link
  SHOULD — operating procedures for incident, BCP, DR scenarios

**Freshness cadence:**
- A.5.35 + A.5.36: per-record freshness=365 on the primary leaf
  (each review report/record has its own currency — annual cycle
  doctrine)
- A.5.37: freshness=365 on the review leaf only (the register
  itself is operational and continuously maintained; the annual
  review checks the catalogue)
- All review leaves: 365d (matches the records-family default
  established by A.5.33 batch 17 + A.5.34 batch 18)

**Lifecycle-end variant catalog now:**
Phase B has accumulated a rich set of lifecycle-end variants —
- A.5.7 per-product intelligence record (threat intel)
- A.5.8 closure_record (ownership transfer)
- A.5.11 return_record (HR offboarding)
- A.5.13 application_record (per-platform)
- A.5.16 revocation_record (identity)
- A.5.17 revocation_record (credential)
- A.5.22 change_response_log (supplier change)
- A.5.24 exercise_record (drills)
- A.5.25 triage_decision (per-event)
- A.5.26 incident_closure_record (per-incident)
- A.5.28 disposal_record (evidence custody end)
- A.5.29 plan_activation_record (HYBRID real+test)
- A.5.30 recovery_record (HYBRID real+test)
- A.5.33 (none — pure 3-sibling register/scope/review)
- A.5.34 (none — pure 3-sibling register/scope/review)
- **A.5.35 finding_response_register** (NEW — finding lifecycle from
  raised → response → closed)
- **A.5.36 nonconformity_register** (NEW — NC lifecycle with root
  cause for systemic improvement)
- A.5.37 (none — pure 3-sibling procedure/scope/review)

The finding_response_register / nonconformity_register pattern is
new this batch — both are lifecycle-end variants for review-record-
as-primary controls (the lifecycle is the finding's journey from
raised to closed, not a per-event physical action).

**End of A.5.3x — what's next:**
With A.5.35/36/37 promoted, the A.5 Organisational Controls block
is fully multi-leaf except A.5.18 (Access rights — the original
case #1 control). Natural next steps:
- **A.5.18** — Access rights (case #1, the OG NC for Arion).
  Currently single-leaf, would close the A.5 arc completely.
- **A.6 People Controls** — A.6.1-6.7 are all single-leaf curated
  via batches 7 (Phase B 2026-05-22). Candidates for multi-leaf
  promotion.
- **A.7 Physical Controls** — A.7.1-7.14 all single-leaf curated
  via batch 7. Similar candidates.
- **A.8 Technological Controls** — large set, mixed multi-leaf
  status (A.8.2/A.8.11/A.8.24/A.8.25/A.8.26/A.8.27 already multi-
  leaf; rest single-leaf).

Multi-control batching pattern is now proven — bundle by spine
variant + conceptual family. Could pursue A.6 (7 controls) or
A.7 (14 controls) as bulk batches with reduced per-control overhead.
