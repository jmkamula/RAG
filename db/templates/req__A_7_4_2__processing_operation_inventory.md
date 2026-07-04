---
leaf_id: req:A.7.4.2:processing_operation_inventory
control_ref: A.7.4.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processing Operation Inventory

> Per-operation row — the ways PII is used inside the org (queries + reports + analytics + ML training + exports). Each row cites the necessity rationale + access controls. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.2:processing_operation_inventory -->
<!-- column: item:A.7.4.2:reg_operation_id -->
<!-- column: item:A.7.4.2:reg_operation_type -->
<!-- column: item:A.7.4.2:reg_purpose_link -->
<!-- column: item:A.7.4.2:reg_pii_scope -->
<!-- column: item:A.7.4.2:reg_access_group -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.2:processing_operation_inventory -->
| Reg Operation Id | Reg Operation Type | Reg Purpose Link | Reg Pii Scope | Reg Access Group |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.2:processing_operation_inventory -->

## Column guidance — what to fill in

### Reg Operation Id

<<MUST item:A.7.4.2:reg_operation_id>>
_Why: Referenceability_

> _Standard text:_ Unique operation identifier per row

### Reg Operation Type

<<MUST item:A.7.4.2:reg_operation_type>>
_Why: Coverage_

> _Standard text:_ Operation type per row (query / report / analytics / ML training / export / integration)

### Reg Purpose Link

<<MUST item:A.7.4.2:reg_purpose_link>>
_Why: §7.4.2 — for identified purposes_

> _Standard text:_ Purpose link per row (A.7.2.1)

### Reg Pii Scope

<<MUST item:A.7.4.2:reg_pii_scope>>
_Why: Coverage_

> _Standard text:_ PII scope per row (which fields / categories)

### Reg Access Group

<<MUST item:A.7.4.2:reg_access_group>>
_Why: §7.4.2 — who can access_

> _Standard text:_ Access group per row (which internal roles can perform this operation)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Reviewed

<<SHOULD item:A.7.4.2:reg_last_reviewed>>
_Why: Currency_

> _Standard text:_ Last necessity-review date per row
