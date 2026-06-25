---
leaf_id: req:A.7.11:utilities_program_review
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Utilities Program Review

> Annual verification of test outcomes, redundancy currency, vendor-SLA performance. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.11:utilities_program_review -->
<!-- column: item:A.7.11:rev_date -->
<!-- column: item:A.7.11:rev_reviewer -->
<!-- column: item:A.7.11:rev_test_outcomes -->
<!-- column: item:A.7.11:rev_vendor_sla -->
<!-- column: item:A.7.11:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.11:utilities_program_review -->
| Rev Date | Rev Reviewer | Rev Test Outcomes | Rev Vendor Sla | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.11:utilities_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.11:rev_date>>
_Why: 27002:7.11 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.11:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec + BCP lead)

### Rev Test Outcomes

<<MUST item:A.7.11:rev_test_outcomes>>
_Why: Continuity validation_

> _Standard text:_ Per-utility test outcomes review (UPS/generator tests in period — pass/fail/remediation)

### Rev Vendor Sla

<<MUST item:A.7.11:rev_vendor_sla>>
_Why: 27002:7.11 — maintenance_

> _Standard text:_ Vendor-SLA review (response times against SLA, breach incidents)

### Rev Register Update

<<MUST item:A.7.11:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the register / procedure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.11:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
