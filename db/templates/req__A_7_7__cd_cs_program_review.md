---
leaf_id: req:A.7.7:cd_cs_program_review
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Clear Desk / Clear Screen Program Review

<<DOC_CONTROL>>

> Annual review of policy currency, audit findings trend, enforcement consistency. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.7:cd_cs_program_review -->
<!-- column: item:A.7.7:rev_date -->
<!-- column: item:A.7.7:rev_reviewer -->
<!-- column: item:A.7.7:rev_audit_trend -->
<!-- column: item:A.7.7:rev_policy_drift -->
<!-- column: item:A.7.7:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your annual reviews for clear desk and clear screen policies, making it easier to demonstrate compliance and spot trends in enforcement or audit findings.

## When to use it

Use this template whenever you need to review your clear desk and clear screen program, which should be done about once a year as part of your ongoing compliance efforts.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes some time to fill out and summarize your findings.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.7:cd_cs_program_review -->
| Rev Date | Rev Reviewer | Rev Audit Trend | Rev Policy Drift | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.7:cd_cs_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.7:rev_date>>
_Why: 27002:7.7 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec + HR partner)

<<GUIDANCE>>

### Rev Audit Trend

<<MUST item:A.7.7:rev_audit_trend>>
_Why: Continual improvement_

> _Standard text:_ Audit-finding trend (improving / worsening — drives policy/awareness adjustments)

<<GUIDANCE>>

### Rev Policy Drift

<<MUST item:A.7.7:rev_policy_drift>>
_Why: Cross-control coherence_

> _Standard text:_ Policy currency check (referenced policies — A.5.12 classification, A.6.7 remote-work — still aligned)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.7:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the policy

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
