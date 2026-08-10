---
leaf_id: req:A.7.14:disposal_program_review
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Disposal Program Review

<<DOC_CONTROL>>

> Annual verification of disposal-record completeness, certificate retention, provider performance. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.14:disposal_program_review -->
<!-- column: item:A.7.14:rev_date -->
<!-- column: item:A.7.14:rev_reviewer -->
<!-- column: item:A.7.14:rev_completeness -->
<!-- column: item:A.7.14:rev_certificate_audit -->
<!-- column: item:A.7.14:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your annual disposal program review, making sure all records are complete, certificates are retained, and providers are performing as expected. It’s useful for meeting ISO 27001 requirements and staying audit-ready.

## When to use it

Use this template once a year to review your disposal program, regardless of your environment. It’s designed for regular, annual checks to ensure ongoing compliance and up-to-date documentation.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes 10-15 minutes to fill out. More time may be needed if you have many disposal providers to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.14:disposal_program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Certificate Audit | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.14:disposal_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.14:rev_date>>
_Why: 27002:7.14 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.14:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT + InfoSec + Legal where regulatory disposal applies)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.7.14:rev_completeness>>
_Why: Cross-control coherence_

> _Standard text:_ Completeness check — every retired asset (from A.5.9) has a matching disposal_record

<<GUIDANCE>>

### Rev Certificate Audit

<<MUST item:A.7.14:rev_certificate_audit>>
_Why: Auditability_

> _Standard text:_ Certificate audit (sample-based verification that retained certificates match register entries)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.14:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.14:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
