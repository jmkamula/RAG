---
leaf_id: req:A.8.6:capacity_monitoring_log
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Capacity Monitoring Log

<<DOC_CONTROL>>

> Continuous evidence stream — resource utilisation samples, threshold breaches, adjustments made. The defence that the baseline was actually in use

<!-- TABLE-COLUMNS leaf:req:A.8.6:capacity_monitoring_log -->
<!-- column: item:A.8.6:log_samples -->
<!-- column: item:A.8.6:log_breaches -->
<!-- column: item:A.8.6:log_actions -->
<!-- column: item:A.8.6:log_retention -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of how your resources are being used, any times they go over set limits, and what actions you take in response. It's useful for showing that your systems are actively in use and monitored.

## When to use it

Use this log continuously in your environment to track resource usage and any adjustments made. Update it as needed whenever there are changes or notable events related to capacity.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40–60 minutes to set up the initial required details, plus additional time for each new entry as you monitor and record ongoing usage.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.6:capacity_monitoring_log -->
| Log Samples | Log Breaches | Log Actions | Log Retention |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.6:capacity_monitoring_log -->

## Column guidance — what to fill in

### Log Samples

<<MUST item:A.8.6:log_samples>>
_Why: 27002:8.6 — monitored_

> _Standard text:_ Resource utilisation samples captured per resource (sub-minute for production)

<<GUIDANCE>>

### Log Breaches

<<MUST item:A.8.6:log_breaches>>
_Why: 27002:8.6 — monitored_

> _Standard text:_ Threshold-breach events logged with timestamp, magnitude, duration

<<GUIDANCE>>

### Log Actions

<<MUST item:A.8.6:log_actions>>
_Why: 27002:8.6 — adjusted_

> _Standard text:_ Actions taken in response to breach captured (auto-scale event / manual scale / accepted)

<<GUIDANCE>>

### Log Retention

<<MUST item:A.8.6:log_retention>>
_Why: A.8.15 linkage_

> _Standard text:_ Log retention period defined and enforced (cross-link to A.8.15)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Trending

<<SHOULD item:A.8.6:log_trending>>
_Why: Forecasting input_

> _Standard text:_ Trending views for capacity planning (weekly / monthly / yearly aggregates)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
