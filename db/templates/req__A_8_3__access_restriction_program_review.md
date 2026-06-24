---
leaf_id: req:A.8.3:access_restriction_program_review
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Access Restriction Program Review

> Annual verification that enforcement still matches the policy, the matrix register reflects reality, and recertification cadence is being met (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.3:rev_date>>
_Why: 27002:8.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT lead + InfoSec lead jointly)

<<MUST item:A.8.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Coverage check — every in-scope system has an up-to-date matrix in the register

<<MUST item:A.8.3:rev_coverage_check>>
_Why: 27002:8.3 — restricted_

<<TEXT>>

## 4. Recertification compliance check — every matrix recertified within cadence

<<MUST item:A.8.3:rev_recert_compliance>>
_Why: Drift prevention_

<<TEXT>>

## 5. Findings propagated to the matrix register / procedure

<<MUST item:A.8.3:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
