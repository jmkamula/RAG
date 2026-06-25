---
leaf_id: req:Art.7:consent_program_review
control_ref: Art.7
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Consent Program Review

> Annual verification that the capture mechanism still meets Art.7 standards, the register is being populated, withdrawal requests are being honoured promptly (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.7:consent_program_review -->
<!-- column: item:Art.7:rev_date -->
<!-- column: item:Art.7:rev_reviewer -->
<!-- column: item:Art.7:rev_mechanism_audit -->
<!-- column: item:Art.7:rev_withdrawal_sla -->
<!-- column: item:Art.7:rev_register_currency -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.7:consent_program_review -->
| Rev Date | Rev Reviewer | Rev Mechanism Audit | Rev Withdrawal Sla | Rev Register Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.7:consent_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.7:rev_date>>
_Why: Art.5.2 — periodic accountability_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO or Privacy Lead + product lead)

### Rev Mechanism Audit

<<MUST item:Art.7:rev_mechanism_audit>>
_Why: Art.7.1-2 — drift detection_

> _Standard text:_ Mechanism audit — capture UI still distinguishable, freely-given, no pre-ticked options

### Rev Withdrawal Sla

<<MUST item:Art.7:rev_withdrawal_sla>>
_Why: Art.7.3_

> _Standard text:_ Withdrawal SLA check — withdrawal requests processed within the published timeline

### Rev Register Currency

<<MUST item:Art.7:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — consent events for all in-scope activities are landing in the register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
