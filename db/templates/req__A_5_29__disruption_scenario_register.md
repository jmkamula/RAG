---
leaf_id: req:A.5.29:disruption_scenario_register
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Disruption Scenario Register

> A.5.29 requires the plan to cover all relevant scenarios — invisible scenarios are the ones that hit unprepared. The register catalogues every in-scope disruption scenario: scenario id, type, severity tier, in-scope controls, fallback path, last-test date, owner. It is the operational record that proves the plan actually covers the org's risk landscape, not just the easy scenarios

<!-- TABLE-COLUMNS leaf:req:A.5.29:disruption_scenario_register -->
<!-- column: item:A.5.29:reg_scenario_id -->
<!-- column: item:A.5.29:reg_type -->
<!-- column: item:A.5.29:reg_severity -->
<!-- column: item:A.5.29:reg_in_scope_ctrls -->
<!-- column: item:A.5.29:reg_fallback -->
<!-- column: item:A.5.29:reg_last_tested -->
<!-- column: item:A.5.29:reg_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.29:disruption_scenario_register -->
| Reg Scenario Id | Reg Type | Reg Severity | Reg In Scope Ctrls | Reg Fallback | Reg Last Tested | Reg Owner |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.29:disruption_scenario_register -->

## Column guidance — what to fill in

### Reg Scenario Id

<<MUST item:A.5.29:reg_scenario_id>>
_Why: 27002:5.29 — scenario coverage_

> _Standard text:_ Each in-scope scenario captured with a unique identifier

### Reg Type

<<MUST item:A.5.29:reg_type>>
_Why: 27002:5.29 — scenario taxonomy_

> _Standard text:_ Scenario type per row (cyber_attack / natural_event / supplier_failure / regulatory_action / personnel_loss / infrastructure_failure)

### Reg Severity

<<MUST item:A.5.29:reg_severity>>
_Why: 27002:5.29 — tier-based response_

> _Standard text:_ Severity tier per row (tier_1_full_disruption / tier_2_partial / tier_3_localised) — drives the activation path

### Reg In Scope Ctrls

<<MUST item:A.5.29:reg_in_scope_ctrls>>
_Why: 27002:5.29 — scope analysis + cross-link to [[A.5.9]]_

> _Standard text:_ In-scope controls per row (which security controls this scenario specifically impacts; cross-link to A.5.9 asset register for assets at risk)

### Reg Fallback

<<MUST item:A.5.29:reg_fallback>>
_Why: 27002:5.29 — appropriate level_

> _Standard text:_ Fallback path per row (which compensating measure activates; what residual risk it accepts)

### Reg Last Tested

<<MUST item:A.5.29:reg_last_tested>>
_Why: 27002:5.29 — preparation cadence_

> _Standard text:_ Last-tested date per row (drives stale-scenario detection — scenarios not exercised in N months flag for refresh)

### Reg Owner

<<MUST item:A.5.29:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per row (accountable for keeping this scenario's plan section current)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Recovery Target

<<SHOULD item:A.5.29:reg_recovery_target>>
_Why: Cross-link to [[A.5.30]]_

> _Standard text:_ Recovery target per row where applicable (RTO/RPO for ICT scenarios — cross-link to A.5.30)

### Reg Supplier Dep

<<SHOULD item:A.5.29:reg_supplier_dep>>
_Why: Cross-link to [[A.5.22]]_

> _Standard text:_ Supplier dependency flag per row where the fallback relies on a specific supplier
