---
leaf_id: req:Art.19:notification_program_review
control_ref: Art.19
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Art.19 Notification Program Review

> Annual verification that every Art.16/17/18 event had a corresponding Art.19 notification record (or documented exception) (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.19:notification_program_review -->
<!-- column: item:Art.19:rev_date -->
<!-- column: item:Art.19:rev_reviewer -->
<!-- column: item:Art.19:rev_event_coverage -->
<!-- column: item:Art.19:rev_exception_validity -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.19:notification_program_review -->
| Rev Date | Rev Reviewer | Rev Event Coverage | Rev Exception Validity |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.19:notification_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.19:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.19:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO)

### Rev Event Coverage

<<MUST item:Art.19:rev_event_coverage>>
_Why: Cross-leaf_

> _Standard text:_ Event coverage check — every Art.16/17/18 event has a register row OR documented exception

### Rev Exception Validity

<<MUST item:Art.19:rev_exception_validity>>
_Why: Defensibility_

> _Standard text:_ Exception validity sample — claimed impossibility/disproportionality grounds still hold

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.19:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
