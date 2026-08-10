---
leaf_id: req:A.8.5:authentication_log
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Authentication Activity Log

<<DOC_CONTROL>>

> Continuous evidence stream — auth events, failure patterns, suspicious-login signals, MFA bypass attempts. Feeds detection (A.8.16) and incident triage (A.5.25)

<!-- TABLE-COLUMNS leaf:req:A.8.5:authentication_log -->
<!-- column: item:A.8.5:log_auth_events -->
<!-- column: item:A.8.5:log_failure_clusters -->
<!-- column: item:A.8.5:log_impossible_travel -->
<!-- column: item:A.8.5:log_mfa_anomalies -->
<!-- column: item:A.8.5:log_retention -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of authentication activities, including failed logins and suspicious access attempts, making it easier to spot unusual patterns and respond to security incidents quickly.

## When to use it

Use this log at all times in your environment, updating it whenever authentication events occur or whenever you notice something unusual that needs to be recorded.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes setting up the initial required elements, with additional time needed as you add new entries for each authentication event.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.5:authentication_log -->
| Log Auth Events | Log Failure Clusters | Log Impossible Travel | Log Mfa Anomalies | Log Retention |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.5:authentication_log -->

## Column guidance — what to fill in

### Log Auth Events

<<MUST item:A.8.5:log_auth_events>>
_Why: 27002:8.5 — implemented_

> _Standard text:_ All authentication events captured (success / failure / MFA challenge / step-up)

<<GUIDANCE>>

### Log Failure Clusters

<<MUST item:A.8.5:log_failure_clusters>>
_Why: Modern baseline_

> _Standard text:_ Failure-cluster detection (brute force, password spraying)

<<GUIDANCE>>

### Log Impossible Travel

<<MUST item:A.8.5:log_impossible_travel>>
_Why: Modern baseline_

> _Standard text:_ Impossible-travel / geo-anomaly detection where applicable

<<GUIDANCE>>

### Log Mfa Anomalies

<<MUST item:A.8.5:log_mfa_anomalies>>
_Why: 27002:8.5 — secure (modern attack vector)_

> _Standard text:_ MFA-prompt fatigue / push-bombing detection

<<GUIDANCE>>

### Log Retention

<<MUST item:A.8.5:log_retention>>
_Why: A.8.15 linkage_

> _Standard text:_ Retention period defined and enforced (cross-link to A.8.15)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Siem Forward

<<SHOULD item:A.8.5:log_siem_forward>>
_Why: Detection maturity_

> _Standard text:_ Events forwarded to SIEM with correlation to identity events (A.5.16)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
