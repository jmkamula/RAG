---
leaf_id: req:A.8.9:configuration_baseline_register
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Configuration Baseline Register

> Catalogue of baselines — per asset class which baseline version is current, last review date, drift-finding count

<!-- TABLE-COLUMNS leaf:req:A.8.9:configuration_baseline_register -->
<!-- column: item:A.8.9:reg_asset_class -->
<!-- column: item:A.8.9:reg_version -->
<!-- column: item:A.8.9:reg_owner -->
<!-- column: item:A.8.9:reg_last_reviewed -->
<!-- column: item:A.8.9:reg_drift_count -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.9:configuration_baseline_register -->
| Reg Asset Class | Reg Version | Reg Owner | Reg Last Reviewed | Reg Drift Count |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.9:configuration_baseline_register -->

## Column guidance — what to fill in

### Reg Asset Class

<<MUST item:A.8.9:reg_asset_class>>
_Why: Identification_

> _Standard text:_ Per-baseline asset class (Linux server / Windows endpoint / K8s cluster / cloud account / network device)

### Reg Version

<<MUST item:A.8.9:reg_version>>
_Why: Drift detection_

> _Standard text:_ Per-baseline current version (semver or date-stamped)

### Reg Owner

<<MUST item:A.8.9:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-baseline named owner (technology lead with InfoSec partner)

### Reg Last Reviewed

<<MUST item:A.8.9:reg_last_reviewed>>
_Why: Drift detection_

> _Standard text:_ Per-baseline last review date

### Reg Drift Count

<<MUST item:A.8.9:reg_drift_count>>
_Why: Continuous evidence_

> _Standard text:_ Per-baseline outstanding drift finding count + open SLA breaches

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg External Ref

<<SHOULD item:A.8.9:reg_external_ref>>
_Why: Defensibility_

> _Standard text:_ External reference (CIS / vendor / NIST) per baseline where applicable
