---
leaf_id: req:A.8.12:dlp_alert_log
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# DLP Alert Log

<<DOC_CONTROL>>

> Continuous evidence stream — alerts triggered, dispositions, true/false-positive trending. Proves the baseline is in active use

<!-- TABLE-COLUMNS leaf:req:A.8.12:dlp_alert_log -->
<!-- column: item:A.8.12:log_alerts -->
<!-- column: item:A.8.12:log_dispositions -->
<!-- column: item:A.8.12:log_classification_breakdown -->
<!-- column: item:A.8.12:log_retention -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of all Data Loss Prevention (DLP) alerts, including how each alert was handled and trends over time. It shows that your DLP controls are actively monitored and managed.

## When to use it

Use this template whenever your environment generates DLP alerts, and update it as new alerts occur or when there are changes in alert handling. It should be kept current to reflect ongoing monitoring.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40–60 minutes setting up the initial log with all required details. After that, adding each new alert will take just a few minutes per entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.12:dlp_alert_log -->
| Log Alerts | Log Dispositions | Log Classification Breakdown | Log Retention |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.12:dlp_alert_log -->

## Column guidance — what to fill in

### Log Alerts

<<MUST item:A.8.12:log_alerts>>
_Why: 27002:8.12 — measures applied_

> _Standard text:_ All DLP alerts captured (channel / rule / classification / user / outcome)

<<GUIDANCE>>

### Log Dispositions

<<MUST item:A.8.12:log_dispositions>>
_Why: Continuous evidence_

> _Standard text:_ Per-alert disposition (false-positive / true-positive remediated / accepted-with-justification / escalated to incident)

<<GUIDANCE>>

### Log Classification Breakdown

<<MUST item:A.8.12:log_classification_breakdown>>
_Why: Operational visibility_

> _Standard text:_ Alert volume broken down by classification (reveals tuning gaps)

<<GUIDANCE>>

### Log Retention

<<MUST item:A.8.12:log_retention>>
_Why: A.8.15 linkage_

> _Standard text:_ Log retention defined and enforced (cross-link to A.8.15)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Siem Forward

<<SHOULD item:A.8.12:log_siem_forward>>
_Why: Detection maturity_

> _Standard text:_ Alerts forwarded to SIEM (cross-link to A.8.16)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
