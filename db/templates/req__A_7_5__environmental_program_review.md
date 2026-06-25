---
leaf_id: req:A.7.5:environmental_program_review
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Environmental Protection Program Review

> Annual review of threat assessments, protection currency, detection-system health, exercise outcomes. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.5:environmental_program_review -->
<!-- column: item:A.7.5:rev_date -->
<!-- column: item:A.7.5:rev_reviewer -->
<!-- column: item:A.7.5:rev_threat_currency -->
<!-- column: item:A.7.5:rev_detection_test -->
<!-- column: item:A.7.5:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5:environmental_program_review -->
| Rev Date | Rev Reviewer | Rev Threat Currency | Rev Detection Test | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5:environmental_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.5:rev_date>>
_Why: 27002:7.5 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec + BCP lead)

### Rev Threat Currency

<<MUST item:A.7.5:rev_threat_currency>>
_Why: 27002:7.5 — current_

> _Standard text:_ Threat-currency check — has the threat landscape shifted (new climate data, regional risk changes)?

### Rev Detection Test

<<MUST item:A.7.5:rev_detection_test>>
_Why: 27002:7.5 — protection_

> _Standard text:_ Detection-system test outcomes (smoke detectors, water-leak sensors functionally tested in the period)

### Rev Register Update

<<MUST item:A.7.5:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the threat register and procedure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
