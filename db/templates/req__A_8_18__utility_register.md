---
leaf_id: req:A.8.18:utility_register
control_ref: A.8.18
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Privileged Utility Programs Register

> Per-utility inventory — utility id, capability, current location, authorised users, last-use

<!-- TABLE-COLUMNS leaf:req:A.8.18:utility_register -->
<!-- column: item:A.8.18:reg_utility_id -->
<!-- column: item:A.8.18:reg_capability -->
<!-- column: item:A.8.18:reg_location -->
<!-- column: item:A.8.18:reg_authorised -->
<!-- column: item:A.8.18:reg_last_use -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.18:utility_register -->
| Reg Utility Id | Reg Capability | Reg Location | Reg Authorised | Reg Last Use |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.18:utility_register -->

## Column guidance — what to fill in

### Reg Utility Id

<<MUST item:A.8.18:reg_utility_id>>
_Why: Identification_

> _Standard text:_ Per-row utility identifier (name + version)

### Reg Capability

<<MUST item:A.8.18:reg_capability>>
_Why: 27002:8.18 — utility programs that can override_

> _Standard text:_ Per-row capability description (what controls it can override)

### Reg Location

<<MUST item:A.8.18:reg_location>>
_Why: 27002:8.18 — restricted_

> _Standard text:_ Per-row current location (systems where installed) — drives removal-where-unneeded principle

### Reg Authorised

<<MUST item:A.8.18:reg_authorised>>
_Why: 27002:8.18 — restricted_

> _Standard text:_ Per-row authorised user list (with approval lineage)

### Reg Last Use

<<MUST item:A.8.18:reg_last_use>>
_Why: Drift detection_

> _Standard text:_ Per-row last-use timestamp (drives 'still needed' review)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Jit Vault

<<SHOULD item:A.8.18:reg_jit_vault>>
_Why: Modern maturity_

> _Standard text:_ Per-row JIT-vault availability flag (where applicable, indicates non-standing-install path)
