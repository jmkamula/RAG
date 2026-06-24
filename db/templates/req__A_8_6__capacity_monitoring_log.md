---
leaf_id: req:A.8.6:capacity_monitoring_log
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Capacity Monitoring Log

> Continuous evidence stream — resource utilisation samples, threshold breaches, adjustments made. The defence that the baseline was actually in use

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Resource utilisation samples captured per resource (sub-minute for production)

<<MUST item:A.8.6:log_samples>>
_Why: 27002:8.6 — monitored_

<<TEXT>>

## 2. Threshold-breach events logged with timestamp, magnitude, duration

<<MUST item:A.8.6:log_breaches>>
_Why: 27002:8.6 — monitored_

<<TEXT>>

## 3. Actions taken in response to breach captured (auto-scale event / manual scale / accepted)

<<MUST item:A.8.6:log_actions>>
_Why: 27002:8.6 — adjusted_

<<TEXT>>

## 4. Log retention period defined and enforced (cross-link to A.8.15)

<<MUST item:A.8.6:log_retention>>
_Why: A.8.15 linkage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trending views for capacity planning (weekly / monthly / yearly aggregates)

<<SHOULD item:A.8.6:log_trending>>
_Why: Forecasting input_

<<TEXT>>
