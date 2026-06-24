---
leaf_id: req:A.5.8:project_security_register
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Project Security Register

> A.5.8 requires every project to be visible to the security function — invisible projects are the ones that miss gates. The register catalogues every in-scope project: id, name, security tier, current stage, owner, InfoSec liaison, planned closure date, status. It is the operational record that proves the gate process is actually applied org-wide, not just on the projects InfoSec happens to hear about

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each in-scope project captured with a unique identifier

<<MUST item:A.5.8:reg_project_id>>
_Why: 27002:5.8 — visibility_

<<TEXT>>

## 2. Security tier per row (drives which gates apply — full / lightweight / waived-with-justification)

<<MUST item:A.5.8:reg_tier>>
_Why: 27002:5.8 — proportionality_

<<TEXT>>

## 3. Current stage per row (initiation / requirements / build / pre-go-live / live / closed) updated as gates are passed

<<MUST item:A.5.8:reg_stage>>
_Why: 27002:5.8 — lifecycle tracking_

<<TEXT>>

## 4. Project owner per row (named individual accountable for delivery + security)

<<MUST item:A.5.8:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. InfoSec liaison per row (named individual reviewing this project's security gates)

<<MUST item:A.5.8:reg_infosec_liaison>>
_Why: 27002:5.8 — defined responsibilities_

<<TEXT>>

## 6. SDLC link per row where project involves software development (cross-ref to A.8.25 / A.8.26 outputs)

<<MUST item:A.5.8:reg_sdlc_link>>
_Why: 27002:5.8 + cross-link to [[A.8.25]] / [[A.8.26]]_

<<TEXT>>

## 7. Planned closure date per row (drives the closure-gate trigger)

<<MUST item:A.5.8:reg_planned_closure>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Supplier-agreement link per row where project triggers new third-party contracts (cross-ref to A.5.20)

<<SHOULD item:A.5.8:reg_supplier_link>>
_Why: Closing loop with [[A.5.20]]_

<<TEXT>>

### 2. Cloud-service link per row where project introduces a new cloud service (cross-ref to A.5.23 cloud register)

<<SHOULD item:A.5.8:reg_cloud_link>>
_Why: Closing loop with [[A.5.23]]_

<<TEXT>>
