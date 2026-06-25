---
leaf_id: req:A.5.8:project_security_register
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Project Security Register

> A.5.8 requires every project to be visible to the security function — invisible projects are the ones that miss gates. The register catalogues every in-scope project: id, name, security tier, current stage, owner, InfoSec liaison, planned closure date, status. It is the operational record that proves the gate process is actually applied org-wide, not just on the projects InfoSec happens to hear about

<!-- TABLE-COLUMNS leaf:req:A.5.8:project_security_register -->
<!-- column: item:A.5.8:reg_project_id -->
<!-- column: item:A.5.8:reg_tier -->
<!-- column: item:A.5.8:reg_stage -->
<!-- column: item:A.5.8:reg_owner -->
<!-- column: item:A.5.8:reg_infosec_liaison -->
<!-- column: item:A.5.8:reg_sdlc_link -->
<!-- column: item:A.5.8:reg_planned_closure -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.8:project_security_register -->
| Reg Project Id | Reg Tier | Reg Stage | Reg Owner | Reg Infosec Liaison | Reg Sdlc Link | Reg Planned Closure |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.8:project_security_register -->

## Column guidance — what to fill in

### Reg Project Id

<<MUST item:A.5.8:reg_project_id>>
_Why: 27002:5.8 — visibility_

> _Standard text:_ Each in-scope project captured with a unique identifier

### Reg Tier

<<MUST item:A.5.8:reg_tier>>
_Why: 27002:5.8 — proportionality_

> _Standard text:_ Security tier per row (drives which gates apply — full / lightweight / waived-with-justification)

### Reg Stage

<<MUST item:A.5.8:reg_stage>>
_Why: 27002:5.8 — lifecycle tracking_

> _Standard text:_ Current stage per row (initiation / requirements / build / pre-go-live / live / closed) updated as gates are passed

### Reg Owner

<<MUST item:A.5.8:reg_owner>>
_Why: Accountability_

> _Standard text:_ Project owner per row (named individual accountable for delivery + security)

### Reg Infosec Liaison

<<MUST item:A.5.8:reg_infosec_liaison>>
_Why: 27002:5.8 — defined responsibilities_

> _Standard text:_ InfoSec liaison per row (named individual reviewing this project's security gates)

### Reg Sdlc Link

<<MUST item:A.5.8:reg_sdlc_link>>
_Why: 27002:5.8 + cross-link to [[A.8.25]] / [[A.8.26]]_

> _Standard text:_ SDLC link per row where project involves software development (cross-ref to A.8.25 / A.8.26 outputs)

### Reg Planned Closure

<<MUST item:A.5.8:reg_planned_closure>>
_Why: Operational discipline_

> _Standard text:_ Planned closure date per row (drives the closure-gate trigger)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Supplier Link

<<SHOULD item:A.5.8:reg_supplier_link>>
_Why: Closing loop with [[A.5.20]]_

> _Standard text:_ Supplier-agreement link per row where project triggers new third-party contracts (cross-ref to A.5.20)

### Reg Cloud Link

<<SHOULD item:A.5.8:reg_cloud_link>>
_Why: Closing loop with [[A.5.23]]_

> _Standard text:_ Cloud-service link per row where project introduces a new cloud service (cross-ref to A.5.23 cloud register)
