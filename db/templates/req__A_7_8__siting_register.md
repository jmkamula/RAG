---
leaf_id: req:A.7.8:siting_register
control_ref: A.7.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Equipment Siting Register

<<DOC_CONTROL>>

> The catalogue of in-scope equipment with location, class, protection measures applied, owner

<!-- TABLE-COLUMNS leaf:req:A.7.8:siting_register -->
<!-- column: item:A.7.8:reg_equipment_id -->
<!-- column: item:A.7.8:reg_location -->
<!-- column: item:A.7.8:reg_class -->
<!-- column: item:A.7.8:reg_protection -->
<!-- column: item:A.7.8:reg_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an organized list of all important equipment, showing where it is, what type it is, who is responsible, and what protections are in place.

## When to use it

Use this register whenever you need to track equipment in your environment, and update it whenever there are changes to your equipment or its details.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per item for the required details, plus extra time for each piece of equipment you add to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.8:siting_register -->
| Reg Equipment Id | Reg Location | Reg Class | Reg Protection | Reg Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.8:siting_register -->

## Column guidance — what to fill in

### Reg Equipment Id

<<MUST item:A.7.8:reg_equipment_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row equipment identifier (cross-link to A.5.9 asset register)

<<GUIDANCE>>

### Reg Location

<<MUST item:A.7.8:reg_location>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row location (site + room per A.7.3 register)

<<GUIDANCE>>

### Reg Class

<<MUST item:A.7.8:reg_class>>
_Why: 27002:7.8 — proportional_

> _Standard text:_ Per-row equipment class (drives required protection level)

<<GUIDANCE>>

### Reg Protection

<<MUST item:A.7.8:reg_protection>>
_Why: 27002:7.8 — implemented_

> _Standard text:_ Per-row protection measures in place (matches procedure's per-class requirements)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.7.8:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row owner

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Remediation

<<SHOULD item:A.7.8:reg_remediation>>
_Why: Operational discipline_

> _Standard text:_ Per-row remediation log where protection falls short of required

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
