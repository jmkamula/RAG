---
leaf_id: req:5.2:isp_program_review
control_ref: 5.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Information Security Policy Program Review

<<DOC_CONTROL>>

> Annual verification that the policy is current, approved, and communicated; that approval records are complete; that communication evidence is in date (freshness=365)

<!-- TABLE-COLUMNS leaf:req:5.2:isp_program_review -->
<!-- column: item:5.2:rev_date -->
<!-- column: item:5.2:rev_reviewer -->
<!-- column: item:5.2:rev_policy_currency -->
<!-- column: item:5.2:rev_approval_currency -->
<!-- column: item:5.2:rev_comms_completeness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your Information Security Policy is up-to-date, properly approved, and effectively communicated, with clear records for annual compliance checks.

## When to use it

Use this review record once a year to verify your policy’s approval status and communication, ensuring your documentation stays current and meets ISO 27001 requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how quickly you can gather and record the required information.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.2:isp_program_review -->
| Rev Date | Rev Reviewer | Rev Policy Currency | Rev Approval Currency | Rev Comms Completeness |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.2:isp_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:5.2:rev_date>>
_Why: Clause 5.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:5.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + top management sponsor)

<<GUIDANCE>>

### Rev Policy Currency

<<MUST item:5.2:rev_policy_currency>>
_Why: Drift detection_

> _Standard text:_ Policy currency check — still appropriate to organisational purpose and scope

<<GUIDANCE>>

### Rev Approval Currency

<<MUST item:5.2:rev_approval_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Approval currency check — signed by current top management

<<GUIDANCE>>

### Rev Comms Completeness

<<MUST item:5.2:rev_comms_completeness>>
_Why: Cross-leaf coherence_

> _Standard text:_ Communication completeness check — required audience is covered and current

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:5.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
