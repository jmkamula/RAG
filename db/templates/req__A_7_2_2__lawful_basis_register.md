---
leaf_id: req:A.7.2.2:lawful_basis_register
control_ref: A.7.2.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Lawful Basis Register

> Per-activity lawful basis record — the documented basis for every processing activity. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.2:lawful_basis_register -->
<!-- column: item:A.7.2.2:reg_activity_id -->
<!-- column: item:A.7.2.2:reg_primary_basis -->
<!-- column: item:A.7.2.2:reg_special_category_basis -->
<!-- column: item:A.7.2.2:reg_lia_reference -->
<!-- column: item:A.7.2.2:reg_purpose_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.2:lawful_basis_register -->
| Reg Activity Id | Reg Primary Basis | Reg Special Category Basis | Reg Lia Reference | Reg Purpose Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.2:lawful_basis_register -->

## Column guidance — what to fill in

### Reg Activity Id

<<MUST item:A.7.2.2:reg_activity_id>>
_Why: Traceability_

> _Standard text:_ Processing activity identifier per row

### Reg Primary Basis

<<MUST item:A.7.2.2:reg_primary_basis>>
_Why: §7.2.2 — documented_

> _Standard text:_ Primary basis cited per row (Art.6.1.a-f or equivalent)

### Reg Special Category Basis

<<MUST item:A.7.2.2:reg_special_category_basis>>
_Why: GDPR Art.9.2_

> _Standard text:_ Special-category basis where applicable (Art.9.2.a-j / Art.10 basis)

### Reg Lia Reference

<<MUST item:A.7.2.2:reg_lia_reference>>
_Why: Art.6.1.f — balancing test recorded_

> _Standard text:_ LIA reference per row where basis is legitimate interests

### Reg Purpose Link

<<MUST item:A.7.2.2:reg_purpose_link>>
_Why: §7.2.1 cross-link_

> _Standard text:_ Purpose link (which A.7.2.1 purpose(s) this basis authorises)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Basis Date

<<SHOULD item:A.7.2.2:reg_basis_date>>
_Why: Currency_

> _Standard text:_ Date basis established / last re-evaluated
