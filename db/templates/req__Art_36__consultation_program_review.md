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
---

# Art.36 Prior Consultation Program Review

> Annual verification — every residual-high-risk DPIA escalated to SA, advice acted on, waiting periods respected (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.36:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal)

<<MUST item:Art.36:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Escalation audit — every Art.35 DPIA flagging residual high risk has a corresponding Art.36 consultation row

<<MUST item:Art.36:rev_escalation_audit>>
_Why: Cross-article_

<<TEXT>>

## 4. Waiting-period compliance — no processing started before SA waiting period elapsed

<<MUST item:Art.36:rev_waiting_compliance>>
_Why: Art.36.2_

<<TEXT>>

## 5. Advice handling sample — SA written advice incorporated or formally rejected with rationale recorded

<<MUST item:Art.36:rev_advice_handling>>
_Why: Art.36.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.36:rev_next_date>>
_Why: Planning_

<<TEXT>>
