---
leaf_id: req:A.5.30:ict_service_register
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# ICT Service Continuity Register

> A.5.30 requires every in-scope ICT service to have a defined recovery posture — invisible services are the ones that don't come back when the org needs them. The register catalogues every in-scope ICT service: service id, criticality tier, RTO/RPO targets, dependencies, recovery owner, last-tested date. It is the operational record that proves the plan covers the org's ACTUAL service inventory, not just the easy-to-restore subset

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each in-scope ICT service captured with a unique identifier

<<MUST item:A.5.30:reg_service_id>>
_Why: 27002:5.30 — visibility_

<<TEXT>>

## 2. Criticality tier per row (tier_1_mission_critical / tier_2_business_critical / tier_3_supporting) — drives RTO/RPO selection

<<MUST item:A.5.30:reg_criticality>>
_Why: 27002:5.30 — BIA tiering_

<<TEXT>>

## 3. RTO/RPO targets per row (specific numeric values, not 'best effort')

<<MUST item:A.5.30:reg_rto_rpo>>
_Why: 27002:5.30 — business continuity objectives_

<<TEXT>>

## 4. Service dependencies per row (upstream + downstream — recovery order matters; recover dependencies first)

<<MUST item:A.5.30:reg_dependencies>>
_Why: 27002:5.30 — readiness coordination_

<<TEXT>>

## 5. Named recovery owner per row (technical lead accountable for the service's recovery, not just IT generally)

<<MUST item:A.5.30:reg_recovery_owner>>
_Why: Accountability_

<<TEXT>>

## 6. Last-tested date per row (drives stale-test detection — services not tested in N months flag for refresh)

<<MUST item:A.5.30:reg_last_tested>>
_Why: 27002:5.30 — preparation cadence_

<<TEXT>>

## 7. Asset-link per row (cross-link to A.5.9 asset register entries that constitute this service)

<<MUST item:A.5.30:reg_asset_link>>
_Why: 27002:5.30 + cross-link to [[A.5.9]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Supplier dependency flag per row where recovery depends on supplier action (cross-link to A.5.21 / A.5.22)

<<SHOULD item:A.5.30:reg_supplier_dep>>
_Why: Cross-link to [[A.5.22]]_

<<TEXT>>

### 2. Data residency note per row where backup geographic separation has jurisdictional implications (cross-link to A.5.14 transfer policy)

<<SHOULD item:A.5.30:reg_data_residency>>
_Why: Cross-link to [[A.5.14]]_

<<TEXT>>
