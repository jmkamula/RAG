---
leaf_id: req:A.7.6:secure_work_program_review
control_ref: A.7.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Secure Work Program Review

> Annual verification that secure-area rules are being followed, session register has no gaps, and incidents (escort failure, device intrusion) are captured. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.6:secure_work_program_review -->
<!-- column: item:A.7.6:rev_date -->
<!-- column: item:A.7.6:rev_reviewer -->
<!-- column: item:A.7.6:rev_compliance_check -->
<!-- column: item:A.7.6:rev_incidents -->
<!-- column: item:A.7.6:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.6:secure_work_program_review -->
| Rev Date | Rev Reviewer | Rev Compliance Check | Rev Incidents | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.6:secure_work_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.6:rev_date>>
_Why: 27002:7.6 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec)

### Rev Compliance Check

<<MUST item:A.7.6:rev_compliance_check>>
_Why: 27002:7.6 — effectiveness_

> _Standard text:_ Compliance sampling — sessions verified against permit/escort/device-restriction rules

### Rev Incidents

<<MUST item:A.7.6:rev_incidents>>
_Why: Continual improvement_

> _Standard text:_ Incidents review (escort failures, device-intrusion events) — closure status

### Rev Register Update

<<MUST item:A.7.6:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
