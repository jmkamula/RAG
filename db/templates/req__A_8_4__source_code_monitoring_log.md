---
leaf_id: req:A.8.4:source_code_monitoring_log
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Source Code Access Monitoring Log

> Continuous evidence stream — repository access events, branch-protection bypass attempts, secrets-scanner hits, dependency-scanner findings

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Repository access events captured (clone / push / admin actions)

<<MUST item:A.8.4:log_repo_events>>
_Why: 27002:8.4 — appropriately managed_

<<TEXT>>

## 2. Secrets-scanner findings logged with disposition (false-positive / true-positive remediated)

<<MUST item:A.8.4:log_secrets_hits>>
_Why: 27002:8.4 — appropriately managed_

<<TEXT>>

## 3. Dependency-scanner findings logged with remediation SLA

<<MUST item:A.8.4:log_dep_findings>>
_Why: 27002:8.4 — software libraries_

<<TEXT>>

## 4. Branch-protection bypass attempts captured (admin override events)

<<MUST item:A.8.4:log_bypass_attempts>>
_Why: Anomaly signal_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Events forwarded to SIEM (cross-link to A.8.16)

<<SHOULD item:A.8.4:log_siem_forward>>
_Why: Detection maturity_

<<TEXT>>
