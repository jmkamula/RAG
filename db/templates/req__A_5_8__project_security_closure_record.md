---
leaf_id: req:A.5.8:project_security_closure_record
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Per-Project Security Closure Record

> A.5.8 expects each project to formally close out security — not just go-live and dissolve the team. The closure record evidences the handover gate: project id, gates passed, outstanding risks transferred to operations with named owner, security artefacts archived, and final signoff. One record per closed project, traceable back to the project register and through to operational ownership

<!-- TABLE-COLUMNS leaf:req:A.5.8:project_security_closure_record -->
<!-- column: item:A.5.8:cls_project_ref -->
<!-- column: item:A.5.8:cls_gates_passed -->
<!-- column: item:A.5.8:cls_residual_risks -->
<!-- column: item:A.5.8:cls_artefacts_archived -->
<!-- column: item:A.5.8:cls_signoff -->
<!-- column: item:A.5.8:cls_closure_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.8:project_security_closure_record -->
| Cls Project Ref | Cls Gates Passed | Cls Residual Risks | Cls Artefacts Archived | Cls Signoff | Cls Closure Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.8:project_security_closure_record -->

## Column guidance — what to fill in

### Cls Project Ref

<<MUST item:A.5.8:cls_project_ref>>
_Why: 27002:5.8 — traceability_

> _Standard text:_ Project identifier per record (links to project register)

### Cls Gates Passed

<<MUST item:A.5.8:cls_gates_passed>>
_Why: 27002:5.8 — lifecycle closure_

> _Standard text:_ Gates-passed summary per record (which gates closed and when; gaps explicitly noted with risk acceptance)

### Cls Residual Risks

<<MUST item:A.5.8:cls_residual_risks>>
_Why: 27002:5.8 — risk acceptance + transfer_

> _Standard text:_ Residual-risk register transfer per record (outstanding risks named, accepted by named operational owner with date)

### Cls Artefacts Archived

<<MUST item:A.5.8:cls_artefacts_archived>>
_Why: Audit defensibility_

> _Standard text:_ Security artefacts archived per record (threat model, pen-test report, DPIA where applicable, exception register)

### Cls Signoff

<<MUST item:A.5.8:cls_signoff>>
_Why: 27002:5.8 — closure handover_

> _Standard text:_ Final signoff per record (project sponsor + InfoSec gate-owner + operational owner — three-way)

### Cls Closure Date

<<MUST item:A.5.8:cls_closure_date>>
_Why: Operational discipline_

> _Standard text:_ Closure date recorded

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Cls Supplier Handover

<<SHOULD item:A.5.8:cls_supplier_handover>>
_Why: Closing loop with [[A.5.22]]_

> _Standard text:_ Supplier-agreement handover per record where project introduced new third-party contracts (operational owner takes A.5.22 review duty)

### Cls Lessons Link

<<SHOULD item:A.5.8:cls_lessons_link>>
_Why: Closing loop with [[A.5.27]]_

> _Standard text:_ Lessons-learned link per record where project surfaced patterns worth feeding into A.5.27 lessons register
