---
leaf_id: req:A.8.32:change_program_review
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Change Management Program Review

> Annual verification — register completeness, emergency-change ratio, rollback-attainment, change-induced-incident trending (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.32:change_program_review -->
<!-- column: item:A.8.32:rev_date -->
<!-- column: item:A.8.32:rev_reviewer -->
<!-- column: item:A.8.32:rev_register_completeness -->
<!-- column: item:A.8.32:rev_emergency_ratio -->
<!-- column: item:A.8.32:rev_change_incidents -->
<!-- column: item:A.8.32:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.32:change_program_review -->
| Rev Date | Rev Reviewer | Rev Register Completeness | Rev Emergency Ratio | Rev Change Incidents | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.32:change_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.32:rev_date>>
_Why: 27002:8.32 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.32:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Change Management lead + Engineering + InfoSec)

### Rev Register Completeness

<<MUST item:A.8.32:rev_register_completeness>>
_Why: Drift prevention_

> _Standard text:_ Register-completeness sample (sample of production changes traced to register)

### Rev Emergency Ratio

<<MUST item:A.8.32:rev_emergency_ratio>>
_Why: Operational signal_

> _Standard text:_ Emergency-change ratio (high ratio signals process bypass)

### Rev Change Incidents

<<MUST item:A.8.32:rev_change_incidents>>
_Why: Continuous improvement_

> _Standard text:_ Change-induced incident trending (cross-link to A.5.26 register — change as incident root cause)

### Rev Findings Update

<<MUST item:A.8.32:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.32:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
