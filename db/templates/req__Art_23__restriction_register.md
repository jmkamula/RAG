---
leaf_id: req:Art.23:restriction_register
control_ref: Art.23
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.23 Restriction Application Register

> Per-invocation record — every time an Art.23 restriction is applied to deny / limit a subject right. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.23:restriction_register -->
<!-- column: item:Art.23:reg_invocation_id -->
<!-- column: item:Art.23:reg_law_citation -->
<!-- column: item:Art.23:reg_right_restricted -->
<!-- column: item:Art.23:reg_purpose -->
<!-- column: item:Art.23:reg_subject_notice -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.23:restriction_register -->
| Reg Invocation Id | Reg Law Citation | Reg Right Restricted | Reg Purpose | Reg Subject Notice |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.23:restriction_register -->

## Column guidance — what to fill in

### Reg Invocation Id

<<MUST item:Art.23:reg_invocation_id>>
_Why: Audit_

> _Standard text:_ Unique invocation identifier per row

### Reg Law Citation

<<MUST item:Art.23:reg_law_citation>>
_Why: Art.23.1_

> _Standard text:_ Per-row Member State law cited (article + section)

### Reg Right Restricted

<<MUST item:Art.23:reg_right_restricted>>
_Why: Art.23.1_

> _Standard text:_ Per-row right restricted (Art.12-22 + Art.34)

### Reg Purpose

<<MUST item:Art.23:reg_purpose>>
_Why: Art.23.1_

> _Standard text:_ Per-row Art.23.1 a-j purpose

### Reg Subject Notice

<<MUST item:Art.23:reg_subject_notice>>
_Why: Art.23.2.h_

> _Standard text:_ Per-row subject notice (where required by Art.23.2.h)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:Art.23:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Per-row legal counsel sign-off
