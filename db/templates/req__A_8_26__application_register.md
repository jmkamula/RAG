---
leaf_id: req:A.8.26:application_register
control_ref: A.8.26
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Application Security Requirements Register

> Per-application catalogue — application id, requirements set applied, approval lineage, traceability status

<!-- TABLE-COLUMNS leaf:req:A.8.26:application_register -->
<!-- column: item:A.8.26:reg_app_id -->
<!-- column: item:A.8.26:reg_requirements_set -->
<!-- column: item:A.8.26:reg_approval -->
<!-- column: item:A.8.26:reg_traceability_status -->
<!-- column: item:A.8.26:reg_classification -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.26:application_register -->
| Reg App Id | Reg Requirements Set | Reg Approval | Reg Traceability Status | Reg Classification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.26:application_register -->

## Column guidance — what to fill in

### Reg App Id

<<MUST item:A.8.26:reg_app_id>>
_Why: Identification_

> _Standard text:_ Per-row application identifier

### Reg Requirements Set

<<MUST item:A.8.26:reg_requirements_set>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row requirements set applied (which categories from the procedure)

### Reg Approval

<<MUST item:A.8.26:reg_approval>>
_Why: Accountability_

> _Standard text:_ Per-row approval lineage (who approved + when)

### Reg Traceability Status

<<MUST item:A.8.26:reg_traceability_status>>
_Why: 27002:8.26 — specified_

> _Standard text:_ Per-row traceability status (requirements-to-test-cases coverage %)

### Reg Classification

<<MUST item:A.8.26:reg_classification>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row data-classification footprint

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Threat Model Ref

<<SHOULD item:A.8.26:reg_threat_model_ref>>
_Why: Defensibility_

> _Standard text:_ Per-row threat-model reference (link to artefact)
