---
leaf_id: req:A.8.5:authentication_program_review
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Authentication Program Review

> Periodic verification that authentication baseline still matches threat landscape, exception inventory is current, and the log shows expected hygiene (freshness=180; auth attack patterns evolve fast)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.5:rev_date>>
_Why: 27002:8.5 — periodic_

<<TEXT>>

## 2. Reviewer identity (IAM lead + InfoSec lead jointly)

<<MUST item:A.8.5:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Threat-landscape review (new attack patterns since last review — feed from threat intel A.5.7)

<<MUST item:A.8.5:rev_threat_landscape>>
_Why: 27002:8.5 — secure (currency)_

<<TEXT>>

## 4. Exception inventory re-confirmed / retired

<<MUST item:A.8.5:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 5. Anomaly-detection outcomes reviewed (true-positive rate, missed-detection postmortems)

<<MUST item:A.8.5:rev_anomaly_outcomes>>
_Why: Detection effectiveness_

<<TEXT>>

## 6. Baseline / procedure updates published from findings

<<MUST item:A.8.5:rev_baseline_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.5:rev_next_date>>
_Why: Planning_

<<TEXT>>
