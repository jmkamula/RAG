---
leaf_id: req:B.8.5.6:subcontractor_disclosure_register
control_ref: B.8.5.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Subcontractor Disclosure Register

> Per-subcontractor-per-customer row — the audit trail of subcontractor disclosures. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.6:subcontractor_disclosure_register -->
<!-- column: item:B.8.5.6:reg_subcontractor_id -->
<!-- column: item:B.8.5.6:reg_customer_id -->
<!-- column: item:B.8.5.6:reg_disclosure_date -->
<!-- column: item:B.8.5.6:reg_countries -->
<!-- column: item:B.8.5.6:reg_disclosure_mode -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.6:subcontractor_disclosure_register -->
| Reg Subcontractor Id | Reg Customer Id | Reg Disclosure Date | Reg Countries | Reg Disclosure Mode |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.6:subcontractor_disclosure_register -->

## Column guidance — what to fill in

### Reg Subcontractor Id

<<MUST item:B.8.5.6:reg_subcontractor_id>>
_Why: Referenceability_

> _Standard text:_ Subcontractor identifier per row

### Reg Customer Id

<<MUST item:B.8.5.6:reg_customer_id>>
_Why: Traceability_

> _Standard text:_ Customer per row

### Reg Disclosure Date

<<MUST item:B.8.5.6:reg_disclosure_date>>
_Why: §8.5.6 — before use_

> _Standard text:_ Disclosure date per row (pre-use)

### Reg Countries

<<MUST item:B.8.5.6:reg_countries>>
_Why: §8.5.6 — countries_

> _Standard text:_ Countries + international orgs disclosed per row

### Reg Disclosure Mode

<<MUST item:B.8.5.6:reg_disclosure_mode>>
_Why: §8.5.6_

> _Standard text:_ Disclosure mode per row (public trust page / DPA schedule / NDA + on-request)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Ack

<<SHOULD item:B.8.5.6:reg_customer_ack>>
_Why: Confirmation_

> _Standard text:_ Customer acknowledgement per row
