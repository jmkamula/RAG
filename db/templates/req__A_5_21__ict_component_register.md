---
leaf_id: req:A.5.21:ict_component_register
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# ICT Component / Vendor Register

> A.5.21 requires the org to know which ICT components are in use, who supplies them, which are critical, when they reach end-of-life, and what sub-suppliers stand behind them. The register is the live source of truth — feeding the periodic review and EOL-replacement leaves

<!-- TABLE-COLUMNS leaf:req:A.5.21:ict_component_register -->
<!-- column: item:A.5.21:reg_component -->
<!-- column: item:A.5.21:reg_critical_flag -->
<!-- column: item:A.5.21:reg_eol_date -->
<!-- column: item:A.5.21:reg_subsupplier -->
<!-- column: item:A.5.21:reg_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.21:ict_component_register -->
| Reg Component | Reg Critical Flag | Reg Eol Date | Reg Subsupplier | Reg Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.21:ict_component_register -->

## Column guidance — what to fill in

### Reg Component

<<MUST item:A.5.21:reg_component>>
_Why: 27002:5.21e — track_

> _Standard text:_ Component / service identified per row (vendor, product, version)

### Reg Critical Flag

<<MUST item:A.5.21:reg_critical_flag>>
_Why: 27002:5.21e_

> _Standard text:_ Critical-component flag per row (drives 27002:5.21e scrutiny)

### Reg Eol Date

<<MUST item:A.5.21:reg_eol_date>>
_Why: 27002:5.21i_

> _Standard text:_ End-of-support / end-of-life date per row

### Reg Subsupplier

<<MUST item:A.5.21:reg_subsupplier>>
_Why: 27002:5.21b,c_

> _Standard text:_ Disclosed sub-suppliers / fourth parties per row

### Reg Owner

<<MUST item:A.5.21:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named internal owner per component (typically architecture or platform team)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Sbom Ref

<<SHOULD item:A.5.21:reg_sbom_ref>>
_Why: Modern supply-chain hygiene_

> _Standard text:_ SBOM hash / version reference per software component

### Reg Vendor Check

<<SHOULD item:A.5.21:reg_vendor_check>>
_Why: 27002:5.21a_

> _Standard text:_ Approved-vendor / banned-vendor list check stamp per row
