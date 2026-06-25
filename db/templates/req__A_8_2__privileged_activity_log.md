---
leaf_id: req:A.8.2:privileged_activity_log
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Privileged Activity Log

> A.8.2 requires audit logs of privileged actions. The activity log captures who performed which privileged action, when, on which system — the continuous evidence stream that the procedure was applied (and that anomalies surface for review)

<!-- TABLE-COLUMNS leaf:req:A.8.2:privileged_activity_log -->
<!-- column: item:A.8.2:log_who -->
<!-- column: item:A.8.2:log_what -->
<!-- column: item:A.8.2:log_when -->
<!-- column: item:A.8.2:log_retention -->
<!-- column: item:A.8.2:log_anomaly_alert -->
<!-- column: item:A.8.2:log_tamper_protect -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.2:privileged_activity_log -->
| Log Who | Log What | Log When | Log Retention | Log Anomaly Alert | Log Tamper Protect |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.2:privileged_activity_log -->

## Column guidance — what to fill in

### Log Who

<<MUST item:A.8.2:log_who>>
_Why: 27002:8.2j_

> _Standard text:_ Identity of the privileged user captured per action

### Log What

<<MUST item:A.8.2:log_what>>
_Why: 27002:8.2j_

> _Standard text:_ Action performed captured (command / change / access)

### Log When

<<MUST item:A.8.2:log_when>>
_Why: 27002:8.2j_

> _Standard text:_ Timestamp captured per action

### Log Retention

<<MUST item:A.8.2:log_retention>>
_Why: A.8.15 linkage_

> _Standard text:_ Log retention period defined and enforced

### Log Anomaly Alert

<<MUST item:A.8.2:log_anomaly_alert>>
_Why: Modern baseline — passive logging without alerting fails detect-respond intent (Style v2 promotion)_

> _Standard text:_ Anomaly alerting configured (unusual hours, unusual scope, unusual command)

### Log Tamper Protect

<<MUST item:A.8.2:log_tamper_protect>>
_Why: Defensible evidence (Style v2 promotion)_

> _Standard text:_ Log integrity protection (write-once / SIEM forwarding off-host)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Siem Correlation

<<SHOULD item:A.8.2:log_siem_correlation>>
_Why: Detection maturity_

> _Standard text:_ SIEM correlation rules tuned for privileged-access misuse patterns
