---
leaf_id: req:A.7.12:cabling_program_review
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Cabling Program Review

<<DOC_CONTROL>>

> Annual verification of inspection completeness, register currency, remediation closure. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.12:cabling_program_review -->
<!-- column: item:A.7.12:rev_date -->
<!-- column: item:A.7.12:rev_reviewer -->
<!-- column: item:A.7.12:rev_inspection_coverage -->
<!-- column: item:A.7.12:rev_remediation_closure -->
<!-- column: item:A.7.12:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your cabling inspections, making sure all checks are complete, records are up to date, and any issues have been resolved. It's designed to support your compliance with ISO 27001 requirements.

## When to use it

Use this template whenever you need to review your cabling program, which should happen about once a year. It's relevant for any environment where cabling inspections and records are required.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes filling this out from scratch, depending on the amount of information you need to enter for each required item.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.12:cabling_program_review -->
| Rev Date | Rev Reviewer | Rev Inspection Coverage | Rev Remediation Closure | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.12:cabling_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.12:rev_date>>
_Why: 27002:7.12 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.12:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + Network lead + InfoSec)

<<GUIDANCE>>

### Rev Inspection Coverage

<<MUST item:A.7.12:rev_inspection_coverage>>
_Why: Drift prevention_

> _Standard text:_ Per-run inspection coverage in period (all runs inspected per planned cadence)

<<GUIDANCE>>

### Rev Remediation Closure

<<MUST item:A.7.12:rev_remediation_closure>>
_Why: Operational discipline_

> _Standard text:_ Remediation closure rate from prior period

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.12:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the register / procedure

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.12:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
