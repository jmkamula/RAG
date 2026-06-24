---
leaf_id: req:A.7.4:monitoring_program_review
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Monitoring Program Review

> Annual verification that monitoring is effective (alarms responded to within SLA, anomalies investigated, footage retained correctly). Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.4:rev_date>>
_Why: 27002:7.4 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + SOC + InfoSec)

<<MUST item:A.7.4:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Response-SLA analysis (alarm-to-on-site arrival times measured against SLA)

<<MUST item:A.7.4:rev_response_sla>>
_Why: 27002:7.4 — alert response_

<<TEXT>>

## 4. Coverage check — blind spots remediated? new areas brought into monitoring scope?

<<MUST item:A.7.4:rev_coverage_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Changes propagated to the procedure / scope

<<MUST item:A.7.4:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.4:rev_next_date>>
_Why: Planning_

<<TEXT>>
