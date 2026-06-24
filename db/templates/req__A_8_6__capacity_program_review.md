---
leaf_id: req:A.8.6:capacity_program_review
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Capacity Program Review

> Annual verification that the capacity baseline still matches demand, forecasts are accurate, and the log shows expected hygiene (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.6:rev_date>>
_Why: 27002:8.6 — periodic_

<<TEXT>>

## 2. Reviewer identity (Infrastructure + Finance + Engineering leadership)

<<MUST item:A.8.6:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Forecast-vs-actual accuracy check across the review window

<<MUST item:A.8.6:rev_forecast_accuracy>>
_Why: 27002:8.6 — expected_

<<TEXT>>

## 4. Breach-pattern review (recurring breaches → baseline re-calibration)

<<MUST item:A.8.6:rev_breach_patterns>>
_Why: Drift prevention_

<<TEXT>>

## 5. Baseline / threshold updates published from findings

<<MUST item:A.8.6:rev_baseline_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.6:rev_next_date>>
_Why: Planning_

<<TEXT>>
