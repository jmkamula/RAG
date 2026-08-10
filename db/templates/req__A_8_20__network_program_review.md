---
leaf_id: req:A.8.20:network_program_review
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Network Program Review

<<DOC_CONTROL>>

> Annual architecture review — zone model still appropriate, register reflects reality, monitoring covers all in-scope segments (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.20:network_program_review -->
<!-- column: item:A.8.20:rev_date -->
<!-- column: item:A.8.20:rev_reviewer -->
<!-- column: item:A.8.20:rev_architecture -->
<!-- column: item:A.8.20:rev_register_completeness -->
<!-- column: item:A.8.20:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of your network architecture, ensuring your zone model is still suitable and your network register and monitoring are up to date.

## When to use it

Use this template once a year to record your periodic network program review, making sure your environment’s network controls and documentation remain current and accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of required elements and the amount of detail in your network register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.20:network_program_review -->
| Rev Date | Rev Reviewer | Rev Architecture | Rev Register Completeness | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.20:network_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.20:rev_date>>
_Why: 27002:8.20 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.20:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Network Engineering + InfoSec)

<<GUIDANCE>>

### Rev Architecture

<<MUST item:A.8.20:rev_architecture>>
_Why: 27002:8.20 — managed_

> _Standard text:_ Architecture review — zone model still matches threat landscape + business reality

<<GUIDANCE>>

### Rev Register Completeness

<<MUST item:A.8.20:rev_register_completeness>>
_Why: Drift prevention_

> _Standard text:_ Register-completeness check (every new segment registered)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.20:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / register / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.20:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
