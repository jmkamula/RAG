---
leaf_id: req:A.7.5:environmental_program_review
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Environmental Protection Program Review

> Annual review of threat assessments, protection currency, detection-system health, exercise outcomes. Freshness=365

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.5:rev_date>>
_Why: 27002:7.5 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec + BCP lead)

<<MUST item:A.7.5:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Threat-currency check — has the threat landscape shifted (new climate data, regional risk changes)?

<<MUST item:A.7.5:rev_threat_currency>>
_Why: 27002:7.5 — current_

<<TEXT>>

## 4. Detection-system test outcomes (smoke detectors, water-leak sensors functionally tested in the period)

<<MUST item:A.7.5:rev_detection_test>>
_Why: 27002:7.5 — protection_

<<TEXT>>

## 5. Changes propagated to the threat register and procedure

<<MUST item:A.7.5:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.5:rev_next_date>>
_Why: Planning_

<<TEXT>>
