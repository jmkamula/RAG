---
leaf_id: req:A.8.25:project_register
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Development Project Register

> Per-project SDLC compliance — project id, lifecycle stage, security-checkpoint status, owner

<!-- TABLE-COLUMNS leaf:req:A.8.25:project_register -->
<!-- column: item:A.8.25:reg_project_id -->
<!-- column: item:A.8.25:reg_lifecycle_stage -->
<!-- column: item:A.8.25:reg_checkpoint_status -->
<!-- column: item:A.8.25:reg_owner -->
<!-- column: item:A.8.25:reg_data_classification -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.25:project_register -->
| Reg Project Id | Reg Lifecycle Stage | Reg Checkpoint Status | Reg Owner | Reg Data Classification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.25:project_register -->

## Column guidance — what to fill in

### Reg Project Id

<<MUST item:A.8.25:reg_project_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-project unique identifier (cross-link to A.5.8 project register)

### Reg Lifecycle Stage

<<MUST item:A.8.25:reg_lifecycle_stage>>
_Why: 27002:8.25 — secure development_

> _Standard text:_ Per-project current lifecycle stage (initiation / design / build / test / release / operate)

### Reg Checkpoint Status

<<MUST item:A.8.25:reg_checkpoint_status>>
_Why: 27002:8.25 — applied_

> _Standard text:_ Per-project security-checkpoint status (which gates passed)

### Reg Owner

<<MUST item:A.8.25:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-project named owner (technical lead with security partner)

### Reg Data Classification

<<MUST item:A.8.25:reg_data_classification>>
_Why: GDPR alignment_

> _Standard text:_ Per-project data classification footprint (drives PII-handling rules)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Exception Log

<<SHOULD item:A.8.25:reg_exception_log>>
_Why: Defensibility_

> _Standard text:_ Per-project exception log (waived gates with rationale + compensating controls)
