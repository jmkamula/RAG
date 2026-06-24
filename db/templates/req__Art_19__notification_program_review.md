---
leaf_id: req:Art.19:notification_program_review
control_ref: Art.19
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
---

# Art.19 Notification Program Review

> Annual verification that every Art.16/17/18 event had a corresponding Art.19 notification record (or documented exception) (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.19:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO)

<<MUST item:Art.19:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Event coverage check — every Art.16/17/18 event has a register row OR documented exception

<<MUST item:Art.19:rev_event_coverage>>
_Why: Cross-leaf_

<<TEXT>>

## 4. Exception validity sample — claimed impossibility/disproportionality grounds still hold

<<MUST item:Art.19:rev_exception_validity>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.19:rev_next_date>>
_Why: Planning_

<<TEXT>>
