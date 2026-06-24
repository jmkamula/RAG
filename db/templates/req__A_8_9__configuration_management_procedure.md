---
leaf_id: req:A.8.9:configuration_management_procedure
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Configuration Management Procedure

> A.8.9 requires configurations established, documented, implemented, monitored, reviewed. Procedure documents baseline ownership, deployment, drift detection, approval flow. Baseline register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Baseline authority defined per asset class (who owns each baseline)

<<MUST item:A.8.9:proc_baseline_authority>>
_Why: 27002:8.9 — established_

<<TEXT>>

## 2. Hardening standards referenced (CIS / vendor / internal) per asset class

<<MUST item:A.8.9:proc_hardening_standards>>
_Why: 27002:8.9 — security configurations_

<<TEXT>>

## 3. Deployment process enforcing baseline (IaC / image / config-mgmt tool)

<<MUST item:A.8.9:proc_deployment>>
_Why: 27002:8.9 — implemented_

<<TEXT>>

## 4. Drift detection from baseline (continuous; alerts when out of compliance)

<<MUST item:A.8.9:proc_drift_detection>>
_Why: 27002:8.9 — monitored_

<<TEXT>>

## 5. Cross-link to A.8.32 change management for baseline updates

<<MUST item:A.8.9:proc_change_link>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Approved-deviation register for assets unable to meet baseline (compensating controls + expiry)

<<MUST item:A.8.9:proc_approved_deviations>>
_Why: 27002:8.9 — appropriate_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Infrastructure-as-code pipelines for repeatable deployment

<<SHOULD item:A.8.9:proc_iac_pipelines>>
_Why: Modern practice_

<<TEXT>>
