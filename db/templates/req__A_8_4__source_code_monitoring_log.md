---
leaf_id: req:A.8.4:source_code_monitoring_log
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Source Code Access Monitoring Log

> Continuous evidence stream — repository access events, branch-protection bypass attempts, secrets-scanner hits, dependency-scanner findings

<!-- TABLE-COLUMNS leaf:req:A.8.4:source_code_monitoring_log -->
<!-- column: item:A.8.4:log_repo_events -->
<!-- column: item:A.8.4:log_secrets_hits -->
<!-- column: item:A.8.4:log_dep_findings -->
<!-- column: item:A.8.4:log_bypass_attempts -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.4:source_code_monitoring_log -->
| Log Repo Events | Log Secrets Hits | Log Dep Findings | Log Bypass Attempts |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.4:source_code_monitoring_log -->

## Column guidance — what to fill in

### Log Repo Events

<<MUST item:A.8.4:log_repo_events>>
_Why: 27002:8.4 — appropriately managed_

> _Standard text:_ Repository access events captured (clone / push / admin actions)

### Log Secrets Hits

<<MUST item:A.8.4:log_secrets_hits>>
_Why: 27002:8.4 — appropriately managed_

> _Standard text:_ Secrets-scanner findings logged with disposition (false-positive / true-positive remediated)

### Log Dep Findings

<<MUST item:A.8.4:log_dep_findings>>
_Why: 27002:8.4 — software libraries_

> _Standard text:_ Dependency-scanner findings logged with remediation SLA

### Log Bypass Attempts

<<MUST item:A.8.4:log_bypass_attempts>>
_Why: Anomaly signal_

> _Standard text:_ Branch-protection bypass attempts captured (admin override events)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Siem Forward

<<SHOULD item:A.8.4:log_siem_forward>>
_Why: Detection maturity_

> _Standard text:_ Events forwarded to SIEM (cross-link to A.8.16)
