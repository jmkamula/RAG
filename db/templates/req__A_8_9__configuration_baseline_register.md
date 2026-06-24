---
leaf_id: req:A.8.9:configuration_baseline_register
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Configuration Baseline Register

> Catalogue of baselines — per asset class which baseline version is current, last review date, drift-finding count

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-baseline asset class (Linux server / Windows endpoint / K8s cluster / cloud account / network device)

<<MUST item:A.8.9:reg_asset_class>>
_Why: Identification_

<<TEXT>>

## 2. Per-baseline current version (semver or date-stamped)

<<MUST item:A.8.9:reg_version>>
_Why: Drift detection_

<<TEXT>>

## 3. Per-baseline named owner (technology lead with InfoSec partner)

<<MUST item:A.8.9:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Per-baseline last review date

<<MUST item:A.8.9:reg_last_reviewed>>
_Why: Drift detection_

<<TEXT>>

## 5. Per-baseline outstanding drift finding count + open SLA breaches

<<MUST item:A.8.9:reg_drift_count>>
_Why: Continuous evidence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External reference (CIS / vendor / NIST) per baseline where applicable

<<SHOULD item:A.8.9:reg_external_ref>>
_Why: Defensibility_

<<TEXT>>
