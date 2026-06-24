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
---

# Breach Notification Program Review

> Annual verification that the 72h SLA is being met, severity-gate decisions are defensible, exercises are validating the procedure (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.33:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal + incident-response lead)

<<MUST item:Art.33:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. 72h-compliance audit — every required notification met the SLA (or had documented Art.33.1 delay reason)

<<MUST item:Art.33:rev_72h_compliance>>
_Why: Art.33.1_

<<TEXT>>

## 4. Severity-gate audit — sampled 'no-notify' decisions reviewed for defensibility against Art.33.1 risk threshold

<<MUST item:Art.33:rev_severity_audit>>
_Why: Art.33.1 — risk exception_

<<TEXT>>

## 5. A.5.24 exercise integration — Art.33 procedure exercised within the year (table-top or live)

<<MUST item:Art.33:rev_exercise_link>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.33:rev_next_date>>
_Why: Planning_

<<TEXT>>
