---
leaf_id: req:A.7.3.5:program_review
control_ref: A.7.3.5
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Objection Program Review

> Annual verification — objection channels functional, absolute objections honoured, balancing tests defensible, notification-of-right requirement met (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.5:program_review -->
<!-- column: item:A.7.3.5:rev_date -->
<!-- column: item:A.7.3.5:rev_reviewer -->
<!-- column: item:A.7.3.5:rev_absolute_audit -->
<!-- column: item:A.7.3.5:rev_balancing_audit -->
<!-- column: item:A.7.3.5:rev_notification_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.5:program_review -->
| Rev Date | Rev Reviewer | Rev Absolute Audit | Rev Balancing Audit | Rev Notification Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.5:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.5:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.3.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

### Rev Absolute Audit

<<MUST item:A.7.3.5:rev_absolute_audit>>
_Why: Art.21.3_

> _Standard text:_ Absolute-objection audit — sampled marketing objections verified to have halted processing

### Rev Balancing Audit

<<MUST item:A.7.3.5:rev_balancing_audit>>
_Why: Art.21.1_

> _Standard text:_ Balancing-test audit — sampled rejections reviewed for defensibility

### Rev Notification Audit

<<MUST item:A.7.3.5:rev_notification_audit>>
_Why: Art.21.4_

> _Standard text:_ Notification-of-right audit — first-communication notices reviewed

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
