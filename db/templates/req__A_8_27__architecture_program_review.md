---
leaf_id: req:A.8.27:architecture_program_review
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Architecture Principles Review

<<DOC_CONTROL>>

> Annual verification — principle-set still appropriate, reference-architecture currency, adoption signals (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.27:architecture_program_review -->
<!-- column: item:A.8.27:rev_date -->
<!-- column: item:A.8.27:rev_reviewer -->
<!-- column: item:A.8.27:rev_principle_set -->
<!-- column: item:A.8.27:rev_pattern_currency -->
<!-- column: item:A.8.27:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of whether your architecture principles are still relevant and up to date, and shows how well they are being followed across your systems.

## When to use it

Use this template when your organization needs to confirm, about once a year, that your architecture principles and reference documents are still suitable and being adopted as expected.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this review from scratch, depending on how many principles and adoption signals you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.27:architecture_program_review -->
| Rev Date | Rev Reviewer | Rev Principle Set | Rev Pattern Currency | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.27:architecture_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.27:rev_date>>
_Why: 27002:8.27 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.27:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Chief Architect + Security Architect + InfoSec)

<<GUIDANCE>>

### Rev Principle Set

<<MUST item:A.8.27:rev_principle_set>>
_Why: 27002:8.27 — maintained_

> _Standard text:_ Principle-set review (new threats → new principles; obsolete principles retired)

<<GUIDANCE>>

### Rev Pattern Currency

<<MUST item:A.8.27:rev_pattern_currency>>
_Why: Drift prevention_

> _Standard text:_ Reference-pattern currency check (no abandoned patterns; new technology patterns added)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.27:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.27:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
