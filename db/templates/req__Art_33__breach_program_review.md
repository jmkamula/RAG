---
leaf_id: req:Art.33:breach_program_review
control_ref: Art.33
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Breach Notification Program Review

> Annual verification that the 72h SLA is being met, severity-gate decisions are defensible, exercises are validating the procedure (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.33:breach_program_review -->
<!-- column: item:Art.33:rev_date -->
<!-- column: item:Art.33:rev_reviewer -->
<!-- column: item:Art.33:rev_72h_compliance -->
<!-- column: item:Art.33:rev_severity_audit -->
<!-- column: item:Art.33:rev_exercise_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.33:breach_program_review -->
| Rev Date | Rev Reviewer | Rev 72H Compliance | Rev Severity Audit | Rev Exercise Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.33:breach_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.33:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.33:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal + incident-response lead)

### Rev 72H Compliance

<<MUST item:Art.33:rev_72h_compliance>>
_Why: Art.33.1_

> _Standard text:_ 72h-compliance audit — every required notification met the SLA (or had documented Art.33.1 delay reason)

### Rev Severity Audit

<<MUST item:Art.33:rev_severity_audit>>
_Why: Art.33.1 — risk exception_

> _Standard text:_ Severity-gate audit — sampled 'no-notify' decisions reviewed for defensibility against Art.33.1 risk threshold

### Rev Exercise Link

<<MUST item:Art.33:rev_exercise_link>>
_Why: Cross-control coherence_

> _Standard text:_ A.5.24 exercise integration — Art.33 procedure exercised within the year (table-top or live)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.33:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
