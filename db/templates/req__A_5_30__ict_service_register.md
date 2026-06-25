---
leaf_id: req:A.5.30:ict_service_register
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# ICT Service Continuity Register

> A.5.30 requires every in-scope ICT service to have a defined recovery posture — invisible services are the ones that don't come back when the org needs them. The register catalogues every in-scope ICT service: service id, criticality tier, RTO/RPO targets, dependencies, recovery owner, last-tested date. It is the operational record that proves the plan covers the org's ACTUAL service inventory, not just the easy-to-restore subset

<!-- TABLE-COLUMNS leaf:req:A.5.30:ict_service_register -->
<!-- column: item:A.5.30:reg_service_id -->
<!-- column: item:A.5.30:reg_criticality -->
<!-- column: item:A.5.30:reg_rto_rpo -->
<!-- column: item:A.5.30:reg_dependencies -->
<!-- column: item:A.5.30:reg_recovery_owner -->
<!-- column: item:A.5.30:reg_last_tested -->
<!-- column: item:A.5.30:reg_asset_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.30:ict_service_register -->
| Reg Service Id | Reg Criticality | Reg Rto Rpo | Reg Dependencies | Reg Recovery Owner | Reg Last Tested | Reg Asset Link |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.30:ict_service_register -->

## Column guidance — what to fill in

### Reg Service Id

<<MUST item:A.5.30:reg_service_id>>
_Why: 27002:5.30 — visibility_

> _Standard text:_ Each in-scope ICT service captured with a unique identifier

### Reg Criticality

<<MUST item:A.5.30:reg_criticality>>
_Why: 27002:5.30 — BIA tiering_

> _Standard text:_ Criticality tier per row (tier_1_mission_critical / tier_2_business_critical / tier_3_supporting) — drives RTO/RPO selection

### Reg Rto Rpo

<<MUST item:A.5.30:reg_rto_rpo>>
_Why: 27002:5.30 — business continuity objectives_

> _Standard text:_ RTO/RPO targets per row (specific numeric values, not 'best effort')

### Reg Dependencies

<<MUST item:A.5.30:reg_dependencies>>
_Why: 27002:5.30 — readiness coordination_

> _Standard text:_ Service dependencies per row (upstream + downstream — recovery order matters; recover dependencies first)

### Reg Recovery Owner

<<MUST item:A.5.30:reg_recovery_owner>>
_Why: Accountability_

> _Standard text:_ Named recovery owner per row (technical lead accountable for the service's recovery, not just IT generally)

### Reg Last Tested

<<MUST item:A.5.30:reg_last_tested>>
_Why: 27002:5.30 — preparation cadence_

> _Standard text:_ Last-tested date per row (drives stale-test detection — services not tested in N months flag for refresh)

### Reg Asset Link

<<MUST item:A.5.30:reg_asset_link>>
_Why: 27002:5.30 + cross-link to [[A.5.9]]_

> _Standard text:_ Asset-link per row (cross-link to A.5.9 asset register entries that constitute this service)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Supplier Dep

<<SHOULD item:A.5.30:reg_supplier_dep>>
_Why: Cross-link to [[A.5.22]]_

> _Standard text:_ Supplier dependency flag per row where recovery depends on supplier action (cross-link to A.5.21 / A.5.22)

### Reg Data Residency

<<SHOULD item:A.5.30:reg_data_residency>>
_Why: Cross-link to [[A.5.14]]_

> _Standard text:_ Data residency note per row where backup geographic separation has jurisdictional implications (cross-link to A.5.14 transfer policy)
