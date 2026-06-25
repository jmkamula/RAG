---
leaf_id: req:Art.46:safeguards_register
control_ref: Art.46
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Safeguards Register

> Per-transfer record proving Art.46 safeguard is in place with TIA + supplementary measures where applicable. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.46:safeguards_register -->
<!-- column: item:Art.46:reg_transfer_id -->
<!-- column: item:Art.46:reg_safeguard -->
<!-- column: item:Art.46:reg_sccs_module -->
<!-- column: item:Art.46:reg_tia_outcome -->
<!-- column: item:Art.46:reg_supplementary_measures -->
<!-- column: item:Art.46:reg_signed_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.46:safeguards_register -->
| Reg Transfer Id | Reg Safeguard | Reg Sccs Module | Reg Tia Outcome | Reg Supplementary Measures | Reg Signed Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.46:safeguards_register -->

## Column guidance — what to fill in

### Reg Transfer Id

<<MUST item:Art.46:reg_transfer_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row transfer id (Art.44 register cross-ref)

### Reg Safeguard

<<MUST item:Art.46:reg_safeguard>>
_Why: Art.46.2-3_

> _Standard text:_ Per-row safeguard type (Art.46.2 a-f / Art.46.3 a-b)

### Reg Sccs Module

<<MUST item:Art.46:reg_sccs_module>>
_Why: Commission Decision 2021/914_

> _Standard text:_ Per-row SCC module where applicable (1: C2C / 2: C2P / 3: P2P / 4: P2C)

### Reg Tia Outcome

<<MUST item:Art.46:reg_tia_outcome>>
_Why: Schrems II_

> _Standard text:_ Per-row TIA outcome (acceptable / acceptable-with-supplementary-measures / not-acceptable)

### Reg Supplementary Measures

<<MUST item:Art.46:reg_supplementary_measures>>
_Why: EDPB 01/2020_

> _Standard text:_ Per-row supplementary measures applied (where TIA required)

### Reg Signed Date

<<MUST item:Art.46:reg_signed_date>>
_Why: Currency_

> _Standard text:_ Per-row safeguard signed / countersigned date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Authorisation

<<SHOULD item:Art.46:reg_authorisation>>
_Why: Art.46.3_

> _Standard text:_ Per-row SA authorisation reference (Art.46.3)
