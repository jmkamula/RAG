---
leaf_id: req:Art.42:certification_register
control_ref: Art.42
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Certification Register

> Per-certification record (active + past). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.42:certification_register -->
<!-- column: item:Art.42:reg_certification_id -->
<!-- column: item:Art.42:reg_scheme -->
<!-- column: item:Art.42:reg_scope -->
<!-- column: item:Art.42:reg_valid_until -->
<!-- column: item:Art.42:reg_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.42:certification_register -->
| Reg Certification Id | Reg Scheme | Reg Scope | Reg Valid Until | Reg Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.42:certification_register -->

## Column guidance — what to fill in

### Reg Certification Id

<<MUST item:Art.42:reg_certification_id>>
_Why: Audit_

> _Standard text:_ Per-row certification identifier

### Reg Scheme

<<MUST item:Art.42:reg_scheme>>
_Why: Art.42.5_

> _Standard text:_ Per-row scheme + Art.43 body

### Reg Scope

<<MUST item:Art.42:reg_scope>>
_Why: Art.42.7_

> _Standard text:_ Per-row processing scope covered

### Reg Valid Until

<<MUST item:Art.42:reg_valid_until>>
_Why: Art.42.7_

> _Standard text:_ Per-row validity end date (max 3 years from issue)

### Reg Status

<<MUST item:Art.42:reg_status>>
_Why: Lifecycle_

> _Standard text:_ Per-row status (active / under renewal / withdrawn)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Surveillance Dates

<<SHOULD item:Art.42:reg_surveillance_dates>>
_Why: Cadence_

> _Standard text:_ Per-row surveillance audit dates
