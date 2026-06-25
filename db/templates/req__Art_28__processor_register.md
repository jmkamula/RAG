---
leaf_id: req:Art.28:processor_register
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-Processor DPA Register

> Per-processor record proving every active processor has a signed DPA in force. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.28:processor_register -->
<!-- column: item:Art.28:reg_processor_id -->
<!-- column: item:Art.28:reg_data_categories -->
<!-- column: item:Art.28:reg_dpa_version -->
<!-- column: item:Art.28:reg_subprocessors -->
<!-- column: item:Art.28:reg_security_check -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.28:processor_register -->
| Reg Processor Id | Reg Data Categories | Reg Dpa Version | Reg Subprocessors | Reg Security Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.28:processor_register -->

## Column guidance — what to fill in

### Reg Processor Id

<<MUST item:Art.28:reg_processor_id>>
_Why: Audit defensibility_

> _Standard text:_ Processor identifier per row (entity name, jurisdiction)

### Reg Data Categories

<<MUST item:Art.28:reg_data_categories>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row data categories processed (cross-link to Art.30 RoPA)

### Reg Dpa Version

<<MUST item:Art.28:reg_dpa_version>>
_Why: Currency_

> _Standard text:_ Per-row DPA version + execution date

### Reg Subprocessors

<<MUST item:Art.28:reg_subprocessors>>
_Why: Art.28.2_

> _Standard text:_ Per-row authorised sub-processor list (or 'none')

### Reg Security Check

<<MUST item:Art.28:reg_security_check>>
_Why: Art.28.3c_

> _Standard text:_ Per-row Art.32-equivalent security assurance source (certification / audit report / questionnaire)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Transfer Mechanism

<<SHOULD item:Art.28:reg_transfer_mechanism>>
_Why: Cross-chapter coherence_

> _Standard text:_ Per-row Chap V transfer mechanism where applicable
