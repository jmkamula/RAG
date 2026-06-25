---
leaf_id: req:Art.44:transfer_register
control_ref: Art.44
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# International Transfer Register

> Per-transfer record cataloguing every flow of personal data outside EU/EEA — destination, mechanism, last-assessed date. Drives 'show me every transfer with its safeguard' audit. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.44:transfer_register -->
<!-- column: item:Art.44:reg_transfer_id -->
<!-- column: item:Art.44:reg_data_categories -->
<!-- column: item:Art.44:reg_destination -->
<!-- column: item:Art.44:reg_mechanism -->
<!-- column: item:Art.44:reg_assessed_date -->
<!-- column: item:Art.44:reg_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.44:transfer_register -->
| Reg Transfer Id | Reg Data Categories | Reg Destination | Reg Mechanism | Reg Assessed Date | Reg Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.44:transfer_register -->

## Column guidance — what to fill in

### Reg Transfer Id

<<MUST item:Art.44:reg_transfer_id>>
_Why: Audit_

> _Standard text:_ Per-row unique transfer identifier

### Reg Data Categories

<<MUST item:Art.44:reg_data_categories>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row data categories (cross-link to Art.30 RoPA)

### Reg Destination

<<MUST item:Art.44:reg_destination>>
_Why: Art.44 — third country_

> _Standard text:_ Per-row destination country + recipient entity

### Reg Mechanism

<<MUST item:Art.44:reg_mechanism>>
_Why: Art.44-49 framework_

> _Standard text:_ Per-row Art.45/46/47/49 mechanism cited

### Reg Assessed Date

<<MUST item:Art.44:reg_assessed_date>>
_Why: Currency_

> _Standard text:_ Per-row last-assessed date (drives staleness)

### Reg Owner

<<MUST item:Art.44:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row owner

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Tia Link

<<SHOULD item:Art.44:reg_tia_link>>
_Why: Schrems II_

> _Standard text:_ Per-row link to Transfer Impact Assessment where Schrems II analysis applies
