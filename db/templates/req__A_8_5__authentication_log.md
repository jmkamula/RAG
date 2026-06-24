---
leaf_id: req:A.8.5:authentication_log
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Authentication Activity Log

> Continuous evidence stream — auth events, failure patterns, suspicious-login signals, MFA bypass attempts. Feeds detection (A.8.16) and incident triage (A.5.25)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. All authentication events captured (success / failure / MFA challenge / step-up)

<<MUST item:A.8.5:log_auth_events>>
_Why: 27002:8.5 — implemented_

<<TEXT>>

## 2. Failure-cluster detection (brute force, password spraying)

<<MUST item:A.8.5:log_failure_clusters>>
_Why: Modern baseline_

<<TEXT>>

## 3. Impossible-travel / geo-anomaly detection where applicable

<<MUST item:A.8.5:log_impossible_travel>>
_Why: Modern baseline_

<<TEXT>>

## 4. MFA-prompt fatigue / push-bombing detection

<<MUST item:A.8.5:log_mfa_anomalies>>
_Why: 27002:8.5 — secure (modern attack vector)_

<<TEXT>>

## 5. Retention period defined and enforced (cross-link to A.8.15)

<<MUST item:A.8.5:log_retention>>
_Why: A.8.15 linkage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Events forwarded to SIEM with correlation to identity events (A.5.16)

<<SHOULD item:A.8.5:log_siem_forward>>
_Why: Detection maturity_

<<TEXT>>
