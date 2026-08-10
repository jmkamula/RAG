---
leaf_id: req:A.7.2:entry_program_review
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Entry Program Review

<<DOC_CONTROL>>

> Annual verification that entry controls match area classifications, the register is being maintained, and anomalies are being investigated (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2:entry_program_review -->
<!-- column: item:A.7.2:rev_date -->
<!-- column: item:A.7.2:rev_reviewer -->
<!-- column: item:A.7.2:rev_access_lists -->
<!-- column: item:A.7.2:rev_anomalies -->
<!-- column: item:A.7.2:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your entry controls are appropriate for each area, your entry register is up to date, and any unusual activity is being followed up.

## When to use it

Use this review record once a year to check that your entry program matches your area's needs and that all entries and investigations are properly documented.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of entries and any anomalies that need to be reviewed.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2:entry_program_review -->
| Rev Date | Rev Reviewer | Rev Access Lists | Rev Anomalies | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2:entry_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2:rev_date>>
_Why: 27002:7.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec)

<<GUIDANCE>>

### Rev Access Lists

<<MUST item:A.7.2:rev_access_lists>>
_Why: 27002:7.2 — review_

> _Standard text:_ Per-area access-list review outcome (active / amended / revoked) — cross-link to A.5.18 access review

<<GUIDANCE>>

### Rev Anomalies

<<MUST item:A.7.2:rev_anomalies>>
_Why: Detection_

> _Standard text:_ Anomaly review (flagged events from the register triaged)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.2:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / authorisation lists

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
