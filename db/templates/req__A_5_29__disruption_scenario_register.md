---
leaf_id: req:A.5.29:disruption_scenario_register
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Disruption Scenario Register

> A.5.29 requires the plan to cover all relevant scenarios — invisible scenarios are the ones that hit unprepared. The register catalogues every in-scope disruption scenario: scenario id, type, severity tier, in-scope controls, fallback path, last-test date, owner. It is the operational record that proves the plan actually covers the org's risk landscape, not just the easy scenarios

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each in-scope scenario captured with a unique identifier

<<MUST item:A.5.29:reg_scenario_id>>
_Why: 27002:5.29 — scenario coverage_

<<TEXT>>

## 2. Scenario type per row (cyber_attack / natural_event / supplier_failure / regulatory_action / personnel_loss / infrastructure_failure)

<<MUST item:A.5.29:reg_type>>
_Why: 27002:5.29 — scenario taxonomy_

<<TEXT>>

## 3. Severity tier per row (tier_1_full_disruption / tier_2_partial / tier_3_localised) — drives the activation path

<<MUST item:A.5.29:reg_severity>>
_Why: 27002:5.29 — tier-based response_

<<TEXT>>

## 4. In-scope controls per row (which security controls this scenario specifically impacts; cross-link to A.5.9 asset register for assets at risk)

<<MUST item:A.5.29:reg_in_scope_ctrls>>
_Why: 27002:5.29 — scope analysis + cross-link to [[A.5.9]]_

<<TEXT>>

## 5. Fallback path per row (which compensating measure activates; what residual risk it accepts)

<<MUST item:A.5.29:reg_fallback>>
_Why: 27002:5.29 — appropriate level_

<<TEXT>>

## 6. Last-tested date per row (drives stale-scenario detection — scenarios not exercised in N months flag for refresh)

<<MUST item:A.5.29:reg_last_tested>>
_Why: 27002:5.29 — preparation cadence_

<<TEXT>>

## 7. Named owner per row (accountable for keeping this scenario's plan section current)

<<MUST item:A.5.29:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Recovery target per row where applicable (RTO/RPO for ICT scenarios — cross-link to A.5.30)

<<SHOULD item:A.5.29:reg_recovery_target>>
_Why: Cross-link to [[A.5.30]]_

<<TEXT>>

### 2. Supplier dependency flag per row where the fallback relies on a specific supplier

<<SHOULD item:A.5.29:reg_supplier_dep>>
_Why: Cross-link to [[A.5.22]]_

<<TEXT>>
