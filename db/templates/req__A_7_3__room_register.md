---
leaf_id: req:A.7.3:room_register
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Room Register

> The catalogue of rooms across all sites with classification, locking standard, occupancy controls, owner. Drives 'show me every room is classified and protected per its tier' audit

<!-- TABLE-COLUMNS leaf:req:A.7.3:room_register -->
<!-- column: item:A.7.3:reg_room_id -->
<!-- column: item:A.7.3:reg_classification -->
<!-- column: item:A.7.3:reg_locking -->
<!-- column: item:A.7.3:reg_owner -->
<!-- column: item:A.7.3:reg_last_assessed -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3:room_register -->
| Reg Room Id | Reg Classification | Reg Locking | Reg Owner | Reg Last Assessed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3:room_register -->

## Column guidance — what to fill in

### Reg Room Id

<<MUST item:A.7.3:reg_room_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-room unique identifier

### Reg Classification

<<MUST item:A.7.3:reg_classification>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-room classification (matches procedure's classification scheme)

### Reg Locking

<<MUST item:A.7.3:reg_locking>>
_Why: 27002:7.3 — physical security_

> _Standard text:_ Per-room locking standard in place (matches required standard per classification)

### Reg Owner

<<MUST item:A.7.3:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-room owner (department or named individual responsible)

### Reg Last Assessed

<<MUST item:A.7.3:reg_last_assessed>>
_Why: 27002:7.3 — current_

> _Standard text:_ Per-room last assessment date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Remediation

<<SHOULD item:A.7.3:reg_remediation>>
_Why: Operational discipline_

> _Standard text:_ Remediation log per row where locking falls short of required standard
