---
leaf_id: req:Art.36:consultation_program_review
control_ref: Art.36
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.36 Prior Consultation Program Review

<<DOC_CONTROL>>

> Annual verification — every residual-high-risk DPIA escalated to SA, advice acted on, waiting periods respected (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.36:consultation_program_review -->
<!-- column: item:Art.36:rev_date -->
<!-- column: item:Art.36:rev_reviewer -->
<!-- column: item:Art.36:rev_escalation_audit -->
<!-- column: item:Art.36:rev_waiting_compliance -->
<!-- column: item:Art.36:rev_advice_handling -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of annual reviews for high-risk data protection impact assessments that have been escalated to the supervisory authority, including any advice received and actions taken.

## When to use it

Use this template once a year if you have any high-risk DPIAs that required prior consultation with the supervisory authority, especially when you need to show that you followed their advice and respected any waiting periods.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of required details and the complexity of each high-risk DPIA you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.36:consultation_program_review -->
| Rev Date | Rev Reviewer | Rev Escalation Audit | Rev Waiting Compliance | Rev Advice Handling |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.36:consultation_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.36:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.36:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal)

<<GUIDANCE>>

### Rev Escalation Audit

<<MUST item:Art.36:rev_escalation_audit>>
_Why: Cross-article_

> _Standard text:_ Escalation audit — every Art.35 DPIA flagging residual high risk has a corresponding Art.36 consultation row

<<GUIDANCE>>

### Rev Waiting Compliance

<<MUST item:Art.36:rev_waiting_compliance>>
_Why: Art.36.2_

> _Standard text:_ Waiting-period compliance — no processing started before SA waiting period elapsed

<<GUIDANCE>>

### Rev Advice Handling

<<MUST item:Art.36:rev_advice_handling>>
_Why: Art.36.2_

> _Standard text:_ Advice handling sample — SA written advice incorporated or formally rejected with rationale recorded

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.36:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
