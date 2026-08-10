---
leaf_id: req:5.3:isms_roles_program_review
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# ISMS Roles Program Review

<<DOC_CONTROL>>

> Annual verification that the matrix reflects current org structure, the RACI framework is being followed, and role changes during the year were captured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:5.3:isms_roles_program_review -->
<!-- column: item:5.3:rev_date -->
<!-- column: item:5.3:rev_reviewer -->
<!-- column: item:5.3:rev_currency -->
<!-- column: item:5.3:rev_change_log -->
<!-- column: item:5.3:rev_a52_alignment -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and confirm that your information security roles and responsibilities are up to date and accurately documented, ensuring your team is following the agreed RACI framework.

## When to use it

Use this template once a year to check that your ISMS roles matrix matches your current organization and that any changes in roles have been properly recorded.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of roles and updates needed.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.3:isms_roles_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Change Log | Rev A52 Alignment |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.3:isms_roles_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:5.3:rev_date>>
_Why: Clause 5.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:5.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + HR partner)

<<GUIDANCE>>

### Rev Currency

<<MUST item:5.3:rev_currency>>
_Why: Drift detection_

> _Standard text:_ Matrix currency check — every role still has an active holder

<<GUIDANCE>>

### Rev Change Log

<<MUST item:5.3:rev_change_log>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against change records — every org-chart change touching ISMS roles is logged

<<GUIDANCE>>

### Rev A52 Alignment

<<MUST item:5.3:rev_a52_alignment>>
_Why: Cross-control coherence_

> _Standard text:_ A.5.2 cross-check — operational role definitions still consistent with management-system roles

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:5.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
