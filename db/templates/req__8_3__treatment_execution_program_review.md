---
leaf_id: req:8.3:treatment_execution_program_review
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Treatment Execution Program Review

<<DOC_CONTROL>>

> Semi-annual verification that the plan is being executed on schedule, slipping items get escalated, completed items had residual risk re-affirmed (freshness=180 — operational tempo)

<!-- TABLE-COLUMNS leaf:req:8.3:treatment_execution_program_review -->
<!-- column: item:8.3:rev_date -->
<!-- column: item:8.3:rev_reviewer -->
<!-- column: item:8.3:rev_progress -->
<!-- column: item:8.3:rev_residual_revisit -->
<!-- column: item:8.3:rev_soa_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your treatment plan’s progress, making sure scheduled actions are on track, overdue items are escalated, and completed tasks have their risks reviewed.

## When to use it

Use this review record about every six months to confirm your plan is being followed as intended and to address any delays or unresolved risks in your program.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of items you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.3:treatment_execution_program_review -->
| Rev Date | Rev Reviewer | Rev Progress | Rev Residual Revisit | Rev Soa Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.3:treatment_execution_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:8.3:rev_date>>
_Why: Clause 8.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:8.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Risk Manager + ISMS Manager + ops lead)

<<GUIDANCE>>

### Rev Progress

<<MUST item:8.3:rev_progress>>
_Why: Effectiveness_

> _Standard text:_ Progress check — every active plan item status updated; on-track vs slipping called out

<<GUIDANCE>>

### Rev Residual Revisit

<<MUST item:8.3:rev_residual_revisit>>
_Why: Clause 8.3 — results_

> _Standard text:_ Residual revisit check — completed items had owner re-affirm residual; divergent residuals escalated

<<GUIDANCE>>

### Rev Soa Currency

<<MUST item:8.3:rev_soa_currency>>
_Why: Cross-clause coherence_

> _Standard text:_ SoA currency check — newly implemented controls reflected in the SoA (6.1.3 leaf)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:8.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
