---
leaf_id: req:A.8.11:masking_program_review
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Masking Program Review

<<DOC_CONTROL>>

> Annual verification — masking effectiveness (re-identification residual-risk samples), register currency, exception inventory reviewed (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.11:masking_program_review -->
<!-- column: item:A.8.11:rev_date -->
<!-- column: item:A.8.11:rev_reviewer -->
<!-- column: item:A.8.11:rev_effectiveness -->
<!-- column: item:A.8.11:rev_register_currency -->
<!-- column: item:A.8.11:rev_exception_inventory -->
<!-- column: item:A.8.11:rev_procedure_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of data masking, including how effective your masking is, whether your register is up to date, and if any exceptions need attention.

## When to use it

Use this template once a year to check and record that your data masking program is working as intended and that all related records are current. It applies to every environment you manage.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of entries you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.11:masking_program_review -->
| Rev Date | Rev Reviewer | Rev Effectiveness | Rev Register Currency | Rev Exception Inventory | Rev Procedure Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.11:masking_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.11:rev_date>>
_Why: 27002:8.11 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.11:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Data Engineering + InfoSec)

<<GUIDANCE>>

### Rev Effectiveness

<<MUST item:A.8.11:rev_effectiveness>>
_Why: 27002:8.11 — effective_

> _Standard text:_ Re-identification residual-risk sampling outcome (acceptable or technique upgrade required)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:A.8.11:rev_register_currency>>
_Why: Drift prevention_

> _Standard text:_ Register currency check (refresh timestamps within tolerance)

<<GUIDANCE>>

### Rev Exception Inventory

<<MUST item:A.8.11:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

<<GUIDANCE>>

### Rev Procedure Update

<<MUST item:A.8.11:rev_procedure_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / approved-techniques list

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.11:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
