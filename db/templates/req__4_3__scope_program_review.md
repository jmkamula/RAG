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

> Annual verification that the scope statement reflects current organisational reality and that any scope changes during the year were captured in change records (freshness=365)

<!-- TABLE-COLUMNS leaf:req:4.3:scope_program_review -->
<!-- column: item:4.3:rev_date -->
<!-- column: item:4.3:rev_reviewer -->
<!-- column: item:4.3:rev_currency -->
<!-- column: item:4.3:rev_change_log -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:4.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + top management)

### Rev Currency

<<MUST item:4.3:rev_currency>>
_Why: Drift detection_

> _Standard text:_ Currency check — scope still matches organisational reality (sites, products, third parties)

### Rev Change Log

<<MUST item:4.3:rev_change_log>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against change records — every actual scope change in the year is logged

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:4.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
