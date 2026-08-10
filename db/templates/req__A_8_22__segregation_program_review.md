---
leaf_id: req:A.8.22:segregation_program_review
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Network Segregation Program Review

<<DOC_CONTROL>>

> Annual verification — zone-register completeness, exception inventory current, flow-rules still appropriate, enforcement coverage verified (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.22:segregation_program_review -->
<!-- column: item:A.8.22:rev_date -->
<!-- column: item:A.8.22:rev_reviewer -->
<!-- column: item:A.8.22:rev_register_completeness -->
<!-- column: item:A.8.22:rev_exception_inventory -->
<!-- column: item:A.8.22:rev_enforcement_coverage -->
<!-- column: item:A.8.22:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your network segregation program, making sure your zone register is complete, exceptions are up to date, and enforcement rules are still relevant.

## When to use it

Use this review record once a year to confirm your network zones and controls are current and effective. It applies to any environment where network segregation is in place.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of zones and exceptions you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.22:segregation_program_review -->
| Rev Date | Rev Reviewer | Rev Register Completeness | Rev Exception Inventory | Rev Enforcement Coverage | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.22:segregation_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.22:rev_date>>
_Why: 27002:8.22 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.22:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Network Engineering + InfoSec + Application Engineering leads)

<<GUIDANCE>>

### Rev Register Completeness

<<MUST item:A.8.22:rev_register_completeness>>
_Why: Drift prevention_

> _Standard text:_ Register-completeness check (new zones registered)

<<GUIDANCE>>

### Rev Exception Inventory

<<MUST item:A.8.22:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

<<GUIDANCE>>

### Rev Enforcement Coverage

<<MUST item:A.8.22:rev_enforcement_coverage>>
_Why: 27002:8.22 — segregated_

> _Standard text:_ Sample-based enforcement-coverage verification (configured rules match register)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.22:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.22:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
