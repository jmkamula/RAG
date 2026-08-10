---
leaf_id: req:A.5.2:annual_review
control_ref: A.5.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 3
should_count: 2
table_shape: true
---

# Periodic Roles and Responsibilities Review Record

<<DOC_CONTROL>>

> ISO 27002:2022 § 5.2 implementation guidance treats role allocation as needing periodic review to keep up with organizational change. The review record captures who reviewed the matrix, when, and the outcome (unchanged / re-allocated / new role introduced)

<!-- TABLE-COLUMNS leaf:req:A.5.2:annual_review -->
<!-- column: item:A.5.2:review_date -->
<!-- column: item:A.5.2:review_outcome -->
<!-- column: item:A.5.2:review_reviewer -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of who is responsible for reviewing your organization's roles and responsibilities, when the review took place, and what changes were made, if any. It's useful for staying aligned with ISO 27001 requirements.

## When to use it

Use this document whenever you review your roles and responsibilities matrix, which should happen about once a year or whenever there are significant organizational changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this record from scratch, depending on how many roles you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.2:annual_review -->
| Review Date | Review Outcome | Review Reviewer |
|---|---|---|
|          |          |          |
|          |          |          |
|          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.2:annual_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.2:review_date>>
_Why: 27002:5.2 — periodic review_

> _Standard text:_ Review date within the planned review interval (typically within 12 months of last review)

<<GUIDANCE>>

### Review Outcome

<<MUST item:A.5.2:review_outcome>>
_Why: 27002:5.2_

> _Standard text:_ Outcome of the review (no change / amended to vN / role added or removed)

<<GUIDANCE>>

### Review Reviewer

<<MUST item:A.5.2:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.2:review_triggers>>
_Why: 27002:5.2 — change-driven review_

> _Standard text:_ List of significant-change triggers (reorg, new business line, key role departure) that should prompt an ad-hoc review

<<GUIDANCE>>

### Review Next Date

<<SHOULD item:A.5.2:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
