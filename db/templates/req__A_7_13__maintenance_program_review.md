---
leaf_id: req:A.7.13:maintenance_program_review
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Maintenance Program Review

> Annual verification of cadence compliance, provider performance, post-verification effectiveness. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.13:maintenance_program_review -->
<!-- column: item:A.7.13:rev_date -->
<!-- column: item:A.7.13:rev_reviewer -->
<!-- column: item:A.7.13:rev_cadence_compliance -->
<!-- column: item:A.7.13:rev_provider_performance -->
<!-- column: item:A.7.13:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.13:maintenance_program_review -->
| Rev Date | Rev Reviewer | Rev Cadence Compliance | Rev Provider Performance | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.13:maintenance_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.13:rev_date>>
_Why: 27002:7.13 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.13:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + IT + InfoSec)

### Rev Cadence Compliance

<<MUST item:A.7.13:rev_cadence_compliance>>
_Why: 27002:7.13 — maintained_

> _Standard text:_ Cadence compliance per equipment class (% of due-maintenance actually completed in period)

### Rev Provider Performance

<<MUST item:A.7.13:rev_provider_performance>>
_Why: Supply chain hygiene_

> _Standard text:_ Provider performance review (SLA met / breaches / incident link)

### Rev Register Update

<<MUST item:A.7.13:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.13:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
