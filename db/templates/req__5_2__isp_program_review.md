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

> Annual verification that the policy is current, approved, and communicated; that approval records are complete; that communication evidence is in date (freshness=365)

<!-- TABLE-COLUMNS leaf:req:5.2:isp_program_review -->
<!-- column: item:5.2:rev_date -->
<!-- column: item:5.2:rev_reviewer -->
<!-- column: item:5.2:rev_policy_currency -->
<!-- column: item:5.2:rev_approval_currency -->
<!-- column: item:5.2:rev_comms_completeness -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:5.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + top management sponsor)

### Rev Policy Currency

<<MUST item:5.2:rev_policy_currency>>
_Why: Drift detection_

> _Standard text:_ Policy currency check — still appropriate to organisational purpose and scope

### Rev Approval Currency

<<MUST item:5.2:rev_approval_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Approval currency check — signed by current top management

### Rev Comms Completeness

<<MUST item:5.2:rev_comms_completeness>>
_Why: Cross-leaf coherence_

> _Standard text:_ Communication completeness check — required audience is covered and current

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:5.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
