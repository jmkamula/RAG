---
leaf_id: req:A.7.5.1:transfer_basis_register
control_ref: A.7.5.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Cross-Jurisdiction Transfer Basis Register

> Per-transfer-relationship row — every cross-jurisdiction PII transfer flow with cited basis + jurisdiction pair. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.5.1:transfer_basis_register -->
<!-- column: item:A.7.5.1:reg_transfer_id -->
<!-- column: item:A.7.5.1:reg_origin_jurisdiction -->
<!-- column: item:A.7.5.1:reg_destination_jurisdiction -->
<!-- column: item:A.7.5.1:reg_basis_cited -->
<!-- column: item:A.7.5.1:reg_tia_reference -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.1:transfer_basis_register -->
| Reg Transfer Id | Reg Origin Jurisdiction | Reg Destination Jurisdiction | Reg Basis Cited | Reg Tia Reference |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.1:transfer_basis_register -->

## Column guidance — what to fill in

### Reg Transfer Id

<<MUST item:A.7.5.1:reg_transfer_id>>
_Why: Referenceability_

> _Standard text:_ Unique transfer relationship identifier per row

### Reg Origin Jurisdiction

<<MUST item:A.7.5.1:reg_origin_jurisdiction>>
_Why: Traceability_

> _Standard text:_ Origin jurisdiction per row

### Reg Destination Jurisdiction

<<MUST item:A.7.5.1:reg_destination_jurisdiction>>
_Why: Traceability_

> _Standard text:_ Destination jurisdiction per row

### Reg Basis Cited

<<MUST item:A.7.5.1:reg_basis_cited>>
_Why: §7.5.1 — basis for transfer_

> _Standard text:_ Basis cited per row (Art.45 adequacy / Art.46 SCC / Art.46 BCR / Art.49 derogation / non-EU equivalent)

### Reg Tia Reference

<<MUST item:A.7.5.1:reg_tia_reference>>
_Why: EDPB 01/2020_

> _Standard text:_ TIA reference per row where Art.46 safeguard invoked

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Supplementary Measures

<<SHOULD item:A.7.5.1:reg_supplementary_measures>>
_Why: EDPB 01/2020_

> _Standard text:_ Supplementary measures per row where TIA identified deficiencies
