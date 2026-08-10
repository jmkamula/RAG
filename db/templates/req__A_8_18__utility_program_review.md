---
leaf_id: req:A.8.18:utility_program_review
control_ref: A.8.18
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Privileged Utility Programs Review

<<DOC_CONTROL>>

> Annual verification — register currency, authorised-user list current, removal-where-unneeded sweep, JIT-coverage trending (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.18:utility_program_review -->
<!-- column: item:A.8.18:rev_date -->
<!-- column: item:A.8.18:rev_reviewer -->
<!-- column: item:A.8.18:rev_user_list -->
<!-- column: item:A.8.18:rev_removal_sweep -->
<!-- column: item:A.8.18:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date record of privileged utility programs, showing who is authorized to use them and confirming that only necessary programs remain active. It supports your compliance with ISO 27001 requirements.

## When to use it

Use this template every year to review and update your list of privileged utility programs, ensuring the register is current and all authorized users are accurately listed. It applies to all environments where these programs are used.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of programs and users you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.18:utility_program_review -->
| Rev Date | Rev Reviewer | Rev User List | Rev Removal Sweep | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.18:utility_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.18:rev_date>>
_Why: 27002:8.18 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.18:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec + Infrastructure)

<<GUIDANCE>>

### Rev User List

<<MUST item:A.8.18:rev_user_list>>
_Why: Drift prevention_

> _Standard text:_ Authorised-user list re-confirmed per utility

<<GUIDANCE>>

### Rev Removal Sweep

<<MUST item:A.8.18:rev_removal_sweep>>
_Why: Attack-surface reduction_

> _Standard text:_ Removal-where-unneeded sweep (utilities found in unauthorised locations)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.18:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to register / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.18:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
