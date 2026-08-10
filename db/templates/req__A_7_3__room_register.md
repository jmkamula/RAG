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

<<DOC_CONTROL>>

> The catalogue of rooms across all sites with classification, locking standard, occupancy controls, owner. Drives 'show me every room is classified and protected per its tier' audit

<!-- TABLE-COLUMNS leaf:req:A.7.3:room_register -->
<!-- column: item:A.7.3:reg_room_id -->
<!-- column: item:A.7.3:reg_classification -->
<!-- column: item:A.7.3:reg_locking -->
<!-- column: item:A.7.3:reg_owner -->
<!-- column: item:A.7.3:reg_last_assessed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date list of all rooms at your sites, including details like classification, security measures, and who is responsible for each space. It's useful for demonstrating that every room is properly protected according to its risk level.

## When to use it

Use this register at all times to maintain oversight of your physical spaces, updating it whenever there are changes to rooms, their use, or security features. Refresh the information as needed to ensure accuracy.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each room. Completing the register from scratch can take several hours, depending on the number of rooms you need to document.

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

<<GUIDANCE>>

### Reg Classification

<<MUST item:A.7.3:reg_classification>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-room classification (matches procedure's classification scheme)

<<GUIDANCE>>

### Reg Locking

<<MUST item:A.7.3:reg_locking>>
_Why: 27002:7.3 — physical security_

> _Standard text:_ Per-room locking standard in place (matches required standard per classification)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.7.3:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-room owner (department or named individual responsible)

<<GUIDANCE>>

### Reg Last Assessed

<<MUST item:A.7.3:reg_last_assessed>>
_Why: 27002:7.3 — current_

> _Standard text:_ Per-room last assessment date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Remediation

<<SHOULD item:A.7.3:reg_remediation>>
_Why: Operational discipline_

> _Standard text:_ Remediation log per row where locking falls short of required standard

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
