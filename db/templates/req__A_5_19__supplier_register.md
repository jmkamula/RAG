---
leaf_id: req:A.5.19:supplier_register
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Supplier Register

<<DOC_CONTROL>>

> A.5.19 requires the org to know who its suppliers are, what they provide, the nature of access they hold, and their risk classification. The register is the live source of truth — feeding the periodic review and offboarding leaves

<!-- TABLE-COLUMNS leaf:req:A.5.19:supplier_register -->
<!-- column: item:A.5.19:reg_inventory -->
<!-- column: item:A.5.19:reg_supplier_type -->
<!-- column: item:A.5.19:reg_access_type -->
<!-- column: item:A.5.19:reg_classification -->
<!-- column: item:A.5.19:reg_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date list of all your suppliers, what they do for you, what access they have, and how much risk they pose. It serves as a single, reliable source for supplier information.

## When to use it

Use this register at all times to track your suppliers, updating it whenever you add, change, or remove a supplier. Refresh the information as needed to keep it accurate and current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each supplier. Setting up the register from scratch may take 1-2 hours, depending on how many suppliers you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.19:supplier_register -->
| Reg Inventory | Reg Supplier Type | Reg Access Type | Reg Classification | Reg Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.19:supplier_register -->

## Column guidance — what to fill in

### Reg Inventory

<<MUST item:A.5.19:reg_inventory>>
_Why: 27002:5.19a — types_

> _Standard text:_ Each supplier captured: identity, products/services, criticality

<<GUIDANCE>>

### Reg Supplier Type

<<MUST item:A.5.19:reg_supplier_type>>
_Why: 27002:5.19a_

> _Standard text:_ Supplier type per row (ICT service / ICT infra component / logistics / utilities / etc.)

<<GUIDANCE>>

### Reg Access Type

<<MUST item:A.5.19:reg_access_type>>
_Why: 27002:5.19g_

> _Standard text:_ Access type per row (logical / physical / network / application / app-to-app)

<<GUIDANCE>>

### Reg Classification

<<MUST item:A.5.19:reg_classification>>
_Why: 27002:5.19b,d_

> _Standard text:_ Risk classification (tier or category) per row

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.19:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named internal owner accountable per supplier (relationship owner + InfoSec contact)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Critical Flag

<<SHOULD item:A.5.19:reg_critical_flag>>
_Why: 27002:5.19j_

> _Standard text:_ Critical-supplier flag (drives audit + continuity scrutiny — link to A.5.29 / A.5.30)

<<GUIDANCE>>

### Reg Subsupplier

<<SHOULD item:A.5.19:reg_subsupplier>>
_Why: Supply-chain depth_

> _Standard text:_ Disclosed sub-suppliers / fourth parties tracked per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
