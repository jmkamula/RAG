---
leaf_id: req:Art.18:restriction_register
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Restriction Register

> Per-restriction record proving active restrictions are in place with documented grounds. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.18:restriction_register -->
<!-- column: item:Art.18:reg_subject_id -->
<!-- column: item:Art.18:reg_ground -->
<!-- column: item:Art.18:reg_scope -->
<!-- column: item:Art.18:reg_start_date -->
<!-- column: item:Art.18:reg_lift_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.18:restriction_register -->
| Reg Subject Id | Reg Ground | Reg Scope | Reg Start Date | Reg Lift Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.18:restriction_register -->

## Column guidance — what to fill in

### Reg Subject Id

<<MUST item:Art.18:reg_subject_id>>
_Why: Audit_

> _Standard text:_ Subject identifier per row

### Reg Ground

<<MUST item:Art.18:reg_ground>>
_Why: Art.18.1_

> _Standard text:_ Per-row Art.18.1 ground (a-d) cited

### Reg Scope

<<MUST item:Art.18:reg_scope>>
_Why: Implementation_

> _Standard text:_ Per-row scope (which data, which systems are restricted)

### Reg Start Date

<<MUST item:Art.18:reg_start_date>>
_Why: Currency_

> _Standard text:_ Per-row restriction start date

### Reg Lift Status

<<MUST item:Art.18:reg_lift_status>>
_Why: Art.18.3_

> _Standard text:_ Per-row lift status (active / lifted-on-date with reason)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Art19 Xref

<<SHOULD item:Art.18:reg_art19_xref>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row Art.19 notification reference
