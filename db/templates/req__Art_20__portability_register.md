---
leaf_id: req:Art.20:portability_register
control_ref: Art.20
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Portability Request Register

> Per-request record of Art.20 fulfilments. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.20:portability_register -->
<!-- column: item:Art.20:reg_request_id -->
<!-- column: item:Art.20:reg_applicability_decision -->
<!-- column: item:Art.20:reg_format_delivered -->
<!-- column: item:Art.20:reg_destination -->
<!-- column: item:Art.20:reg_delivery_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.20:portability_register -->
| Reg Request Id | Reg Applicability Decision | Reg Format Delivered | Reg Destination | Reg Delivery Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.20:portability_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.20:reg_request_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row request id (Art.12 register cross-reference)

### Reg Applicability Decision

<<MUST item:Art.20:reg_applicability_decision>>
_Why: Art.20.1_

> _Standard text:_ Per-row applicability decision (in-scope / out-of-scope with grounds)

### Reg Format Delivered

<<MUST item:Art.20:reg_format_delivered>>
_Why: Art.20.1_

> _Standard text:_ Per-row delivered format

### Reg Destination

<<MUST item:Art.20:reg_destination>>
_Why: Art.20.2_

> _Standard text:_ Per-row destination (export to subject / direct controller transmission)

### Reg Delivery Date

<<MUST item:Art.20:reg_delivery_date>>
_Why: Art.12.3_

> _Standard text:_ Per-row delivery date (within Art.12.3 SLA)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Data Volume

<<SHOULD item:Art.20:reg_data_volume>>
_Why: Operational_

> _Standard text:_ Per-row data volume metric (records / bytes)
