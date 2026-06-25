---
leaf_id: req:Art.43:certification_issuance_record
control_ref: Art.43
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Certification Issuance Record

> Per-certificate issuance record. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.43:certification_issuance_record -->
<!-- column: item:Art.43:reg_recipient -->
<!-- column: item:Art.43:reg_assessment -->
<!-- column: item:Art.43:reg_decision_date -->
<!-- column: item:Art.43:reg_grounds -->
<!-- column: item:Art.43:reg_validity -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.43:certification_issuance_record -->
| Reg Recipient | Reg Assessment | Reg Decision Date | Reg Grounds | Reg Validity |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.43:certification_issuance_record -->

## Column guidance — what to fill in

### Reg Recipient

<<MUST item:Art.43:reg_recipient>>
_Why: Audit_

> _Standard text:_ Per-row certificate recipient

### Reg Assessment

<<MUST item:Art.43:reg_assessment>>
_Why: Art.43.2.c_

> _Standard text:_ Per-row assessment outcome with assessor identity

### Reg Decision Date

<<MUST item:Art.43:reg_decision_date>>
_Why: Currency_

> _Standard text:_ Per-row decision date + decision (issue / renew / withdraw / refuse)

### Reg Grounds

<<MUST item:Art.43:reg_grounds>>
_Why: Art.43.5_

> _Standard text:_ Per-row decision grounds (criteria-mapped)

### Reg Validity

<<MUST item:Art.43:reg_validity>>
_Why: Art.42.7_

> _Standard text:_ Per-row validity period (max 3 years per Art.42.7)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Complaint

<<SHOULD item:Art.43:reg_complaint>>
_Why: Art.43.2.d_

> _Standard text:_ Per-row complaint handling where contested
