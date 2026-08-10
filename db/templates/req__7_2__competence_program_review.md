---
leaf_id: req:7.2:competence_program_review
control_ref: 7.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Competence Program Review

<<DOC_CONTROL>>

> Annual verification that the record is current per role, every gap has a closure path, effectiveness is being evaluated for completed actions (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.2:competence_program_review -->
<!-- column: item:7.2:rev_date -->
<!-- column: item:7.2:rev_reviewer -->
<!-- column: item:7.2:rev_currency -->
<!-- column: item:7.2:rev_gap_closure -->
<!-- column: item:7.2:rev_effectiveness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of staff competence records, ensuring each role’s requirements are up to date and any gaps are being addressed with clear follow-up actions.

## When to use it

Use this review record once a year to confirm all competence records are current and effective, and to document closure plans for any identified gaps in your team’s skills or training.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of roles and gaps you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.2:competence_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Gap Closure | Rev Effectiveness |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.2:competence_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:7.2:rev_date>>
_Why: Clause 7.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:7.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR partner + ISMS Manager + relevant function heads)

<<GUIDANCE>>

### Rev Currency

<<MUST item:7.2:rev_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Record currency check — turnover, role changes, new hires reflected

<<GUIDANCE>>

### Rev Gap Closure

<<MUST item:7.2:rev_gap_closure>>
_Why: Effectiveness_

> _Standard text:_ Gap-closure progress check — open gaps either closed or on a remediation plan

<<GUIDANCE>>

### Rev Effectiveness

<<MUST item:7.2:rev_effectiveness>>
_Why: Clause 7.2 c)_

> _Standard text:_ Effectiveness sample — completed actions actually changed observed competence

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:7.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
