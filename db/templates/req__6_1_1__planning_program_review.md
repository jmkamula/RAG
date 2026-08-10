---
leaf_id: req:6.1.1:planning_program_review
control_ref: 6.1.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Planning Program Review

<<DOC_CONTROL>>

> Annual verification that planning inputs are being consumed, the action register is current, effectiveness is being evaluated (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.1.1:planning_program_review -->
<!-- column: item:6.1.1:rev_date -->
<!-- column: item:6.1.1:rev_reviewer -->
<!-- column: item:6.1.1:rev_inputs_currency -->
<!-- column: item:6.1.1:rev_register_currency -->
<!-- column: item:6.1.1:rev_effectiveness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your planning activities, making sure your action register is up to date and that your planning process is working as intended.

## When to use it

Use this document once a year to review your planning program, confirm that planning inputs are being used, and check that your action register and evaluations are current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many items you need to review and update in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.1.1:planning_program_review -->
| Rev Date | Rev Reviewer | Rev Inputs Currency | Rev Register Currency | Rev Effectiveness |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.1.1:planning_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:6.1.1:rev_date>>
_Why: Clause 6.1.1 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:6.1.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + executive sponsor)

<<GUIDANCE>>

### Rev Inputs Currency

<<MUST item:6.1.1:rev_inputs_currency>>
_Why: Cross-clause coherence_

> _Standard text:_ Inputs currency check — 4.1 + 4.2 reviewed before this planning cycle

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:6.1.1:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Action register currency check — every row reviewed for status + relevance

<<GUIDANCE>>

### Rev Effectiveness

<<MUST item:6.1.1:rev_effectiveness>>
_Why: Clause 6.1.1 — evaluate effectiveness_

> _Standard text:_ Effectiveness summary across completed actions

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:6.1.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
