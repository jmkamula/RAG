---
leaf_id: req:A.7.11:utilities_program_review
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Utilities Program Review

> Annual verification of test outcomes, redundancy currency, vendor-SLA performance. Freshness=365

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.11:rev_date>>
_Why: 27002:7.11 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec + BCP lead)

<<MUST item:A.7.11:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-utility test outcomes review (UPS/generator tests in period — pass/fail/remediation)

<<MUST item:A.7.11:rev_test_outcomes>>
_Why: Continuity validation_

<<TEXT>>

## 4. Vendor-SLA review (response times against SLA, breach incidents)

<<MUST item:A.7.11:rev_vendor_sla>>
_Why: 27002:7.11 — maintenance_

<<TEXT>>

## 5. Changes propagated to the register / procedure

<<MUST item:A.7.11:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.11:rev_next_date>>
_Why: Planning_

<<TEXT>>
