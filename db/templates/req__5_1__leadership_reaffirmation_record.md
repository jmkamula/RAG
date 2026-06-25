---
leaf_id: req:5.1:leadership_reaffirmation_record
control_ref: 5.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Leadership Reaffirmation Record

> Per-reaffirmation record capturing each annual (or trigger-based) re-signature of the commitment directive plus evidence of leadership activity in the period. Lifecycle-end artefact: the directive is signed once, but commitment must be visibly renewed

<!-- TABLE-COLUMNS leaf:req:5.1:leadership_reaffirmation_record -->
<!-- column: item:5.1:rea_date -->
<!-- column: item:5.1:rea_signed_by -->
<!-- column: item:5.1:rea_activity_evidence -->
<!-- column: item:5.1:rea_next_due -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.1:leadership_reaffirmation_record -->
| Rea Date | Rea Signed By | Rea Activity Evidence | Rea Next Due |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.1:leadership_reaffirmation_record -->

## Column guidance — what to fill in

### Rea Date

<<MUST item:5.1:rea_date>>
_Why: Currency_

> _Standard text:_ Reaffirmation date stated

### Rea Signed By

<<MUST item:5.1:rea_signed_by>>
_Why: Authenticity_

> _Standard text:_ Signed by current top management (covers turnover)

### Rea Activity Evidence

<<MUST item:5.1:rea_activity_evidence>>
_Why: Clause 5.1 — demonstrate_

> _Standard text:_ Evidence packet for the period (board minutes excerpt, sponsor signoffs, mgmt review attendance)

### Rea Next Due

<<MUST item:5.1:rea_next_due>>
_Why: Planning_

> _Standard text:_ Next reaffirmation due date stated

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rea Trigger

<<SHOULD item:5.1:rea_trigger>>
_Why: Defensible refresh_

> _Standard text:_ Trigger captured if mid-cycle (CEO change, major incident, restructuring)
