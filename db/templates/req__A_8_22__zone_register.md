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

<<DOC_CONTROL>>

> Per-zone catalogue — zone id, classification, contained systems, enforcement boundary, owner

<!-- TABLE-COLUMNS leaf:req:A.8.22:zone_register -->
<!-- column: item:A.8.22:reg_zone_id -->
<!-- column: item:A.8.22:reg_classification -->
<!-- column: item:A.8.22:reg_contained_systems -->
<!-- column: item:A.8.22:reg_enforcement -->
<!-- column: item:A.8.22:reg_exceptions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your network zones, including their IDs, classifications, systems, boundaries, and owners. It's useful for understanding and managing your network security landscape.

## When to use it

Use this register whenever you need to document or review your network zones—it should always be maintained for your environment and updated whenever there are changes to zones or their details.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each network zone. Completing the register from scratch for a typical environment may take 1-2 hours, depending on the number of zones.

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

<<GUIDANCE>>

### Reg Classification

<<MUST item:A.8.22:reg_classification>>
_Why: Cross-control coherence_

> _Standard text:_ Per-zone classification tier

<<GUIDANCE>>

### Reg Contained Systems

<<MUST item:A.8.22:reg_contained_systems>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-zone contained-systems list (drawn from A.5.9)

<<GUIDANCE>>

### Reg Enforcement

<<MUST item:A.8.22:reg_enforcement>>
_Why: 27002:8.22 — segregated_

> _Standard text:_ Per-zone enforcement-boundary description (specific firewall / ACL / policy)

<<GUIDANCE>>

### Reg Exceptions

<<MUST item:A.8.22:reg_exceptions>>
_Why: Drift detection_

> _Standard text:_ Per-zone exception inventory (cross-zone allowances with expiry)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.22:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-zone named owner

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
