---
leaf_id: req:Art.28:processor_program_review
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Processor Program Review

> Annual verification that every active processor has a current DPA, sub-processor authorisations are tracked, Art.32 assurance sources are still valid (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.28:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + procurement / vendor management lead)

<<MUST item:Art.28:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. DPA currency check — every active processor has a current DPA (no expired or pre-onboarding processors active)

<<MUST item:Art.28:rev_dpa_currency>>
_Why: Art.28.3 — written contract_

<<TEXT>>

## 4. Sub-processor audit — every active sub-processor authorised; unauthorised additions flagged

<<MUST item:Art.28:rev_subprocessor_audit>>
_Why: Art.28.2_

<<TEXT>>

## 5. Security assurance currency — Art.32-equivalent evidence (cert, audit) refreshed within validity period

<<MUST item:Art.28:rev_security_currency>>
_Why: Art.28.3c_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.28:rev_next_date>>
_Why: Planning_

<<TEXT>>
