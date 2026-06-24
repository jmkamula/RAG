---
leaf_id: req:Art.8:child_consent_program_review
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Child Consent Program Review

> Annual verification that age-verification and parental-consent flows are functioning, the register is current, no in-scope service is operating without the procedure (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.8:rev_date>>
_Why: Periodic accountability_

<<TEXT>>

## 2. Reviewer identity (DPO + product lead)

<<MUST item:Art.8:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Age-verification sample audit — claimed-age values look plausible vs other signals

<<MUST item:Art.8:rev_verification_quality>>
_Why: Art.8.2 — reasonable efforts_

<<TEXT>>

## 4. Register coverage — every in-scope service has consent rows flowing in

<<MUST item:Art.8:rev_register_coverage>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Member State threshold currency — any MS that has changed its age threshold reflected

<<MUST item:Art.8:rev_threshold_currency>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.8:rev_next_date>>
_Why: Planning_

<<TEXT>>
