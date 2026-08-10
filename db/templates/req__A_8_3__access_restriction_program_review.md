---
leaf_id: req:A.8.3:access_restriction_program_review
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Access Restriction Program Review

<<DOC_CONTROL>>

> Annual verification that enforcement still matches the policy, the matrix register reflects reality, and recertification cadence is being met (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.3:access_restriction_program_review -->
<!-- column: item:A.8.3:rev_date -->
<!-- column: item:A.8.3:rev_reviewer -->
<!-- column: item:A.8.3:rev_coverage_check -->
<!-- column: item:A.8.3:rev_recert_compliance -->
<!-- column: item:A.8.3:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of access restrictions, ensuring your enforcement practices, access matrix, and recertification schedule are up to date and aligned with your policy.

## When to use it

Use this template once a year to confirm that your access restriction program is still effective and accurately documented, as part of your ongoing compliance requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of access entries you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.3:access_restriction_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Recert Compliance | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.3:access_restriction_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.3:rev_date>>
_Why: 27002:8.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT lead + InfoSec lead jointly)

<<GUIDANCE>>

### Rev Coverage Check

<<MUST item:A.8.3:rev_coverage_check>>
_Why: 27002:8.3 — restricted_

> _Standard text:_ Coverage check — every in-scope system has an up-to-date matrix in the register

<<GUIDANCE>>

### Rev Recert Compliance

<<MUST item:A.8.3:rev_recert_compliance>>
_Why: Drift prevention_

> _Standard text:_ Recertification compliance check — every matrix recertified within cadence

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.8.3:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to the matrix register / procedure

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
