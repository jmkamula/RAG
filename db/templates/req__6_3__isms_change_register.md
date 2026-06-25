---
leaf_id: req:6.3:isms_change_register
control_ref: 6.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# ISMS Change Register

> Per-change record capturing every ISMS-level change — the integration point between 4.3 scope changes, 4.4 manual changes, 5.3 roles changes (whose own change records flow up here). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.3:isms_change_register -->
<!-- column: item:6.3:reg_change_id -->
<!-- column: item:6.3:reg_change_type -->
<!-- column: item:6.3:reg_trigger -->
<!-- column: item:6.3:reg_approval -->
<!-- column: item:6.3:reg_impact_summary -->
<!-- column: item:6.3:reg_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.3:isms_change_register -->
| Reg Change Id | Reg Change Type | Reg Trigger | Reg Approval | Reg Impact Summary | Reg Status |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.3:isms_change_register -->

## Column guidance — what to fill in

### Reg Change Id

<<MUST item:6.3:reg_change_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique change identifier per row

### Reg Change Type

<<MUST item:6.3:reg_change_type>>
_Why: Clause 6.3 — determines the need_

> _Standard text:_ Per-row change type (scope / policy / manual / roles / risk-criteria / structural)

### Reg Trigger

<<MUST item:6.3:reg_trigger>>
_Why: Defensibility_

> _Standard text:_ Per-row trigger stated (audit finding, regulator change, org restructure, etc.)

### Reg Approval

<<MUST item:6.3:reg_approval>>
_Why: Clause 6.3 — planned_

> _Standard text:_ Per-row approval signature + date

### Reg Impact Summary

<<MUST item:6.3:reg_impact_summary>>
_Why: Clause 6.3 — consequences_

> _Standard text:_ Per-row impact summary recorded

### Reg Status

<<MUST item:6.3:reg_status>>
_Why: Tracking_

> _Standard text:_ Per-row status (proposed / approved / implemented / withdrawn)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Source Xref

<<SHOULD item:6.3:reg_source_xref>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row cross-reference to the source change record (4.3 / 4.4 / 5.3 etc.) where applicable
