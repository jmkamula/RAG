---
leaf_id: req:Art.34:subject_communication_program_review
control_ref: Art.34
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Art.34 Subject Communication Program Review

> Annual verification — high-risk decisions defensible, exceptions applied appropriately, communication content meets Art.34.2 (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.34:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal + incident-response lead)

<<MUST item:Art.34:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. High-risk decision defensibility — sampled decisions reviewed against criteria

<<MUST item:Art.34:rev_decision_defensibility>>
_Why: Art.34.1_

<<TEXT>>

## 4. Exception-claim audit — Art.34.3 exception claims reviewed for legitimacy (especially encryption-deemed-appropriate where keys may also have been compromised)

<<MUST item:Art.34:rev_exception_audit>>
_Why: Art.34.3_

<<TEXT>>

## 5. Content-quality audit — communications used plain language, included DPO contact, described concrete measures

<<MUST item:Art.34:rev_content_quality>>
_Why: Art.34.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.34:rev_next_date>>
_Why: Planning_

<<TEXT>>
