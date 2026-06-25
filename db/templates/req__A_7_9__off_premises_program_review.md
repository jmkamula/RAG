---
leaf_id: req:A.7.9:off_premises_program_review
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Off-Premises Program Review

> Annual verification that the register is current, theft/loss incidents handled, travel-restriction list still applies. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.9:off_premises_program_review -->
<!-- column: item:A.7.9:rev_date -->
<!-- column: item:A.7.9:rev_reviewer -->
<!-- column: item:A.7.9:rev_register_check -->
<!-- column: item:A.7.9:rev_incident_review -->
<!-- column: item:A.7.9:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.9:off_premises_program_review -->
| Rev Date | Rev Reviewer | Rev Register Check | Rev Incident Review | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.9:off_premises_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.9:rev_date>>
_Why: 27002:7.9 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec + IT lead)

### Rev Register Check

<<MUST item:A.7.9:rev_register_check>>
_Why: Operational discipline_

> _Standard text:_ Stale-loaner check — assets off-premises for unexpectedly long without status update

### Rev Incident Review

<<MUST item:A.7.9:rev_incident_review>>
_Why: 27002:7.9 — protected_

> _Standard text:_ Theft/loss incidents in period — handled per policy, lessons captured

### Rev Register Update

<<MUST item:A.7.9:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the policy / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
