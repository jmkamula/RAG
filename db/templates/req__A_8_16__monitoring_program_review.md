---
leaf_id: req:A.8.16:monitoring_program_review
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 1
---

# Periodic Monitoring Program Review

> Periodic verification — detection coverage gaps, true-positive rate trending, missed-detection postmortems, threat-intel feeding (freshness=180; threat landscape volatile)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.16:rev_date>>
_Why: 27002:8.16 — periodic_

<<TEXT>>

## 2. Reviewer identity (Security Operations lead + InfoSec lead)

<<MUST item:A.8.16:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Coverage check against threat-mapping (any uncovered MITRE technique surfaced)

<<MUST item:A.8.16:rev_coverage>>
_Why: 27002:8.16 — coverage_

<<TEXT>>

## 4. True-positive rate trending review per detection

<<MUST item:A.8.16:rev_tp_trending>>
_Why: Detection effectiveness_

<<TEXT>>

## 5. Missed-detection postmortems reviewed (incidents that bypassed monitoring)

<<MUST item:A.8.16:rev_missed_postmortems>>
_Why: Detection improvement_

<<TEXT>>

## 6. Threat-intel feeding effectiveness (cross-link to A.5.7 — new tactics translated to detections)

<<MUST item:A.8.16:rev_threat_intel_feed>>
_Why: Currency_

<<TEXT>>

## 7. Findings propagated to register / procedure / scope

<<MUST item:A.8.16:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.16:rev_next_date>>
_Why: Planning_

<<TEXT>>
