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

<<DOC_CONTROL>>

> Per-system sync status — system id, current sync source, current drift, last successful sync timestamp

<!-- TABLE-COLUMNS leaf:req:A.8.17:sync_register -->
<!-- column: item:A.8.17:reg_system_id -->
<!-- column: item:A.8.17:reg_source -->
<!-- column: item:A.8.17:reg_drift -->
<!-- column: item:A.8.17:reg_last_sync -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of each system’s clock synchronization status, including which source it uses, any time drift, and when it last synced successfully. It’s useful for maintaining accurate system time records.

## When to use it

Use this register at all times in your environment to monitor clock sync status, updating it whenever there are changes or as needed to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per system for each required detail, so the total time will depend on how many systems you need to document.

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

<<GUIDANCE>>

### Reg Source

<<MUST item:A.8.17:reg_source>>
_Why: 27002:8.17 — synchronized_

> _Standard text:_ Per-row current sync source

<<GUIDANCE>>

### Reg Drift

<<MUST item:A.8.17:reg_drift>>
_Why: Drift detection_

> _Standard text:_ Per-row current drift measurement

<<GUIDANCE>>

### Reg Last Sync

<<MUST item:A.8.17:reg_last_sync>>
_Why: Drift detection_

> _Standard text:_ Per-row last successful sync timestamp

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Alerts

<<SHOULD item:A.8.17:reg_alerts>>
_Why: Operational visibility_

> _Standard text:_ Per-row outstanding alerts (drift exceeded / source lost)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
