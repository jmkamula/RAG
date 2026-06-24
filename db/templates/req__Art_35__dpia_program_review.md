---
leaf_id: req:Art.35:dpia_program_review
control_ref: Art.35
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# DPIA Program Review

> Annual verification — every in-scope activity has a current DPIA, DPO advice was sought, Art.36 consultations escalated where residual risk warranted (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.35:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + executive sponsor + lead privacy engineer)

<<MUST item:Art.35:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Coverage check — every in-scope activity has a current DPIA OR documented Art.35.5 white-list justification

<<MUST item:Art.35:rev_coverage>>
_Why: Art.35.1_

<<TEXT>>

## 4. DPO-advice quality sample — advice substantive, not rubber-stamp

<<MUST item:Art.35:rev_advice_quality>>
_Why: Art.35.2_

<<TEXT>>

## 5. Art.36 escalation audit — residual-high-risk DPIAs escalated to SA where required

<<MUST item:Art.35:rev_art36_audit>>
_Why: Art.36_

<<TEXT>>

## 6. Review-cadence audit — DPIAs refreshed per Art.35.11 when processing changed

<<MUST item:Art.35:rev_review_cadence>>
_Why: Art.35.11_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.35:rev_next_date>>
_Why: Planning_

<<TEXT>>
