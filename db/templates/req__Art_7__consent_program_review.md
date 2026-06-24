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
---

# Consent Program Review

> Annual verification that the capture mechanism still meets Art.7 standards, the register is being populated, withdrawal requests are being honoured promptly (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.7:rev_date>>
_Why: Art.5.2 — periodic accountability_

<<TEXT>>

## 2. Reviewer identity (DPO or Privacy Lead + product lead)

<<MUST item:Art.7:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Mechanism audit — capture UI still distinguishable, freely-given, no pre-ticked options

<<MUST item:Art.7:rev_mechanism_audit>>
_Why: Art.7.1-2 — drift detection_

<<TEXT>>

## 4. Withdrawal SLA check — withdrawal requests processed within the published timeline

<<MUST item:Art.7:rev_withdrawal_sla>>
_Why: Art.7.3_

<<TEXT>>

## 5. Register currency check — consent events for all in-scope activities are landing in the register

<<MUST item:Art.7:rev_register_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.7:rev_next_date>>
_Why: Planning_

<<TEXT>>
