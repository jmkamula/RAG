---
leaf_id: req:A.8.2:privileged_activity_log
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Privileged Activity Log

> A.8.2 requires audit logs of privileged actions. The activity log captures who performed which privileged action, when, on which system — the continuous evidence stream that the procedure was applied (and that anomalies surface for review)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Identity of the privileged user captured per action

<<MUST item:A.8.2:log_who>>
_Why: 27002:8.2j_

<<TEXT>>

## 2. Action performed captured (command / change / access)

<<MUST item:A.8.2:log_what>>
_Why: 27002:8.2j_

<<TEXT>>

## 3. Timestamp captured per action

<<MUST item:A.8.2:log_when>>
_Why: 27002:8.2j_

<<TEXT>>

## 4. Log retention period defined and enforced

<<MUST item:A.8.2:log_retention>>
_Why: A.8.15 linkage_

<<TEXT>>

## 5. Anomaly alerting configured (unusual hours, unusual scope, unusual command)

<<MUST item:A.8.2:log_anomaly_alert>>
_Why: Modern baseline — passive logging without alerting fails detect-respond intent (Style v2 promotion)_

<<TEXT>>

## 6. Log integrity protection (write-once / SIEM forwarding off-host)

<<MUST item:A.8.2:log_tamper_protect>>
_Why: Defensible evidence (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. SIEM correlation rules tuned for privileged-access misuse patterns

<<SHOULD item:A.8.2:log_siem_correlation>>
_Why: Detection maturity_

<<TEXT>>
