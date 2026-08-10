---
leaf_id: req:7.1:resources_program_review
control_ref: 7.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Resources Program Review

<<DOC_CONTROL>>

> Annual verification that resources are commensurate with current ISMS needs, that determined needs were actually provided, that gaps surfaced are being closed (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.1:resources_program_review -->
<!-- column: item:7.1:rev_date -->
<!-- column: item:7.1:rev_reviewer -->
<!-- column: item:7.1:rev_adequacy -->
<!-- column: item:7.1:rev_gap_response -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your information security resources match your current needs, that promised resources were delivered, and that any gaps are being addressed.

## When to use it

Use this template once a year to review your resources and ensure they align with your ISMS requirements. It applies to every environment, regardless of changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 45 to 60 minutes completing this from scratch, depending on the number of resource gaps and details you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.1:resources_program_review -->
| Rev Date | Rev Reviewer | Rev Adequacy | Rev Gap Response |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.1:resources_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:7.1:rev_date>>
_Why: Clause 7.1 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:7.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + finance partner + top management)

<<GUIDANCE>>

### Rev Adequacy

<<MUST item:7.1:rev_adequacy>>
_Why: Clause 7.1 — provide_

> _Standard text:_ Adequacy check — resources actually provided match the determined need per category

<<GUIDANCE>>

### Rev Gap Response

<<MUST item:7.1:rev_gap_response>>
_Why: Effectiveness_

> _Standard text:_ Gap response — any under-resourcing surfaced with remediation plan

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:7.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
