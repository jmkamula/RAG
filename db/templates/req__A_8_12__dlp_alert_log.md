---
leaf_id: req:A.8.12:dlp_alert_log
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# DLP Alert Log

> Continuous evidence stream — alerts triggered, dispositions, true/false-positive trending. Proves the baseline is in active use

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. All DLP alerts captured (channel / rule / classification / user / outcome)

<<MUST item:A.8.12:log_alerts>>
_Why: 27002:8.12 — measures applied_

<<TEXT>>

## 2. Per-alert disposition (false-positive / true-positive remediated / accepted-with-justification / escalated to incident)

<<MUST item:A.8.12:log_dispositions>>
_Why: Continuous evidence_

<<TEXT>>

## 3. Alert volume broken down by classification (reveals tuning gaps)

<<MUST item:A.8.12:log_classification_breakdown>>
_Why: Operational visibility_

<<TEXT>>

## 4. Log retention defined and enforced (cross-link to A.8.15)

<<MUST item:A.8.12:log_retention>>
_Why: A.8.15 linkage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Alerts forwarded to SIEM (cross-link to A.8.16)

<<SHOULD item:A.8.12:log_siem_forward>>
_Why: Detection maturity_

<<TEXT>>
