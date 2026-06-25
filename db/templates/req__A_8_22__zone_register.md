---
leaf_id: req:A.8.22:zone_register
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Network Zone Register

> Per-zone catalogue — zone id, classification, contained systems, enforcement boundary, owner

<!-- TABLE-COLUMNS leaf:req:A.8.22:zone_register -->
<!-- column: item:A.8.22:reg_zone_id -->
<!-- column: item:A.8.22:reg_classification -->
<!-- column: item:A.8.22:reg_contained_systems -->
<!-- column: item:A.8.22:reg_enforcement -->
<!-- column: item:A.8.22:reg_exceptions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.22:zone_register -->
| Reg Zone Id | Reg Classification | Reg Contained Systems | Reg Enforcement | Reg Exceptions |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.22:zone_register -->

## Column guidance — what to fill in

### Reg Zone Id

<<MUST item:A.8.22:reg_zone_id>>
_Why: Identification_

> _Standard text:_ Per-zone unique identifier

### Reg Classification

<<MUST item:A.8.22:reg_classification>>
_Why: Cross-control coherence_

> _Standard text:_ Per-zone classification tier

### Reg Contained Systems

<<MUST item:A.8.22:reg_contained_systems>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-zone contained-systems list (drawn from A.5.9)

### Reg Enforcement

<<MUST item:A.8.22:reg_enforcement>>
_Why: 27002:8.22 — segregated_

> _Standard text:_ Per-zone enforcement-boundary description (specific firewall / ACL / policy)

### Reg Exceptions

<<MUST item:A.8.22:reg_exceptions>>
_Why: Drift detection_

> _Standard text:_ Per-zone exception inventory (cross-zone allowances with expiry)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.22:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-zone named owner
