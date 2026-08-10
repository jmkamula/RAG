---
leaf_id: req:4.3:scope_program_review
control_ref: 4.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# ISMS Scope Program Review

<<DOC_CONTROL>>

> Annual verification that the scope statement reflects current organisational reality and that any scope changes during the year were captured in change records (freshness=365)

<!-- TABLE-COLUMNS leaf:req:4.3:scope_program_review -->
<!-- column: item:4.3:rev_date -->
<!-- column: item:4.3:rev_reviewer -->
<!-- column: item:4.3:rev_currency -->
<!-- column: item:4.3:rev_change_log -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your ISMS scope statement is up to date and accurately reflects your current organization, including any changes made over the past year.

## When to use it

Use this review record once a year to ensure your ISMS scope is still accurate and that all changes have been properly documented, as this is always relevant to your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of changes and details you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.3:scope_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Change Log |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.3:scope_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:4.3:rev_date>>
_Why: Clause 4.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:4.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + top management)

<<GUIDANCE>>

### Rev Currency

<<MUST item:4.3:rev_currency>>
_Why: Drift detection_

> _Standard text:_ Currency check — scope still matches organisational reality (sites, products, third parties)

<<GUIDANCE>>

### Rev Change Log

<<MUST item:4.3:rev_change_log>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against change records — every actual scope change in the year is logged

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:4.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
