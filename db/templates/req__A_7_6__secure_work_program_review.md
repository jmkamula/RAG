---
leaf_id: req:A.7.6:secure_work_program_review
control_ref: A.7.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Secure Work Program Review

> Annual verification that secure-area rules are being followed, session register has no gaps, and incidents (escort failure, device intrusion) are captured. Freshness=365

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.6:rev_date>>
_Why: 27002:7.6 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec)

<<MUST item:A.7.6:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Compliance sampling — sessions verified against permit/escort/device-restriction rules

<<MUST item:A.7.6:rev_compliance_check>>
_Why: 27002:7.6 — effectiveness_

<<TEXT>>

## 4. Incidents review (escort failures, device-intrusion events) — closure status

<<MUST item:A.7.6:rev_incidents>>
_Why: Continual improvement_

<<TEXT>>

## 5. Changes propagated to the procedure

<<MUST item:A.7.6:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.6:rev_next_date>>
_Why: Planning_

<<TEXT>>
