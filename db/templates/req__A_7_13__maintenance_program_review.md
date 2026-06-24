---
leaf_id: req:A.7.13:maintenance_program_review
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Maintenance Program Review

> Annual verification of cadence compliance, provider performance, post-verification effectiveness. Freshness=365

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.13:rev_date>>
_Why: 27002:7.13 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + IT + InfoSec)

<<MUST item:A.7.13:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Cadence compliance per equipment class (% of due-maintenance actually completed in period)

<<MUST item:A.7.13:rev_cadence_compliance>>
_Why: 27002:7.13 — maintained_

<<TEXT>>

## 4. Provider performance review (SLA met / breaches / incident link)

<<MUST item:A.7.13:rev_provider_performance>>
_Why: Supply chain hygiene_

<<TEXT>>

## 5. Changes propagated to the procedure / scope

<<MUST item:A.7.13:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.13:rev_next_date>>
_Why: Planning_

<<TEXT>>
