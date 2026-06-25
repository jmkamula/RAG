---
leaf_id: req:9.2:audit_program_review
control_ref: 9.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Audit Program Review

> Annual verification that the programme is being executed, every planned audit happened (or was deferred with rationale), the cycle stays on track for full coverage (freshness=365)

<!-- TABLE-COLUMNS leaf:req:9.2:audit_program_review -->
<!-- column: item:9.2:rev_date -->
<!-- column: item:9.2:rev_reviewer -->
<!-- column: item:9.2:rev_completion -->
<!-- column: item:9.2:rev_cycle_progress -->
<!-- column: item:9.2:rev_finding_closure -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:9.2:audit_program_review -->
| Rev Date | Rev Reviewer | Rev Completion | Rev Cycle Progress | Rev Finding Closure |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:9.2:audit_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:9.2:rev_date>>
_Why: Clause 9.2 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:9.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + lead auditor)

### Rev Completion

<<MUST item:9.2:rev_completion>>
_Why: Effectiveness_

> _Standard text:_ Completion check — every scheduled audit happened (or deferred with documented reason)

### Rev Cycle Progress

<<MUST item:9.2:rev_cycle_progress>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cycle progress check — at end-of-cycle every ISMS process audited at least once

### Rev Finding Closure

<<MUST item:9.2:rev_finding_closure>>
_Why: Clause 9.2e_

> _Standard text:_ Finding-closure check — last cycle's NCs reached 10.2 closure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:9.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
