---
leaf_id: req:A.8.17:sync_register
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Clock Sync Status Register

> Per-system sync status — system id, current sync source, current drift, last successful sync timestamp

<!-- TABLE-COLUMNS leaf:req:A.8.17:sync_register -->
<!-- column: item:A.8.17:reg_system_id -->
<!-- column: item:A.8.17:reg_source -->
<!-- column: item:A.8.17:reg_drift -->
<!-- column: item:A.8.17:reg_last_sync -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.17:sync_register -->
| Reg System Id | Reg Source | Reg Drift | Reg Last Sync |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.17:sync_register -->

## Column guidance — what to fill in

### Reg System Id

<<MUST item:A.8.17:reg_system_id>>
_Why: Identification_

> _Standard text:_ Per-row system identifier

### Reg Source

<<MUST item:A.8.17:reg_source>>
_Why: 27002:8.17 — synchronized_

> _Standard text:_ Per-row current sync source

### Reg Drift

<<MUST item:A.8.17:reg_drift>>
_Why: Drift detection_

> _Standard text:_ Per-row current drift measurement

### Reg Last Sync

<<MUST item:A.8.17:reg_last_sync>>
_Why: Drift detection_

> _Standard text:_ Per-row last successful sync timestamp

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Alerts

<<SHOULD item:A.8.17:reg_alerts>>
_Why: Operational visibility_

> _Standard text:_ Per-row outstanding alerts (drift exceeded / source lost)
