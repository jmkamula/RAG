---
leaf_id: req:A.8.25:sdlc_program_review
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic SDLC Program Review

> Periodic verification — gate-attainment per project class, exception-inventory current, lifecycle effectiveness (freshness=180; dev practices evolve)

<!-- TABLE-COLUMNS leaf:req:A.8.25:sdlc_program_review -->
<!-- column: item:A.8.25:rev_date -->
<!-- column: item:A.8.25:rev_reviewer -->
<!-- column: item:A.8.25:rev_gate_attainment -->
<!-- column: item:A.8.25:rev_exception_inventory -->
<!-- column: item:A.8.25:rev_lifecycle_effectiveness -->
<!-- column: item:A.8.25:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.25:sdlc_program_review -->
| Rev Date | Rev Reviewer | Rev Gate Attainment | Rev Exception Inventory | Rev Lifecycle Effectiveness | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.25:sdlc_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.25:rev_date>>
_Why: 27002:8.25 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.25:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Engineering leads + InfoSec)

### Rev Gate Attainment

<<MUST item:A.8.25:rev_gate_attainment>>
_Why: 27002:8.25 — applied_

> _Standard text:_ Gate-attainment trending per project class

### Rev Exception Inventory

<<MUST item:A.8.25:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

### Rev Lifecycle Effectiveness

<<MUST item:A.8.25:rev_lifecycle_effectiveness>>
_Why: Closes the loop_

> _Standard text:_ Lifecycle-effectiveness review (incidents that traced to SDLC gaps)

### Rev Findings Update

<<MUST item:A.8.25:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.25:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
