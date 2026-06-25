---
leaf_id: req:A.7.10:media_register
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Storage Media Register

> The catalogue of issued storage media — id, classification, current holder, lifecycle stage. Drives 'where is media X' query and stale-issue detection

<!-- TABLE-COLUMNS leaf:req:A.7.10:media_register -->
<!-- column: item:A.7.10:reg_media_id -->
<!-- column: item:A.7.10:reg_class -->
<!-- column: item:A.7.10:reg_holder -->
<!-- column: item:A.7.10:reg_lifecycle_stage -->
<!-- column: item:A.7.10:reg_issued_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.10:media_register -->
| Reg Media Id | Reg Class | Reg Holder | Reg Lifecycle Stage | Reg Issued Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.10:media_register -->

## Column guidance — what to fill in

### Reg Media Id

<<MUST item:A.7.10:reg_media_id>>
_Why: Lifecycle tracking_

> _Standard text:_ Per-row media identifier (serial/asset tag)

### Reg Class

<<MUST item:A.7.10:reg_class>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row classification (drives encryption + handling requirements)

### Reg Holder

<<MUST item:A.7.10:reg_holder>>
_Why: Accountability_

> _Standard text:_ Per-row current holder

### Reg Lifecycle Stage

<<MUST item:A.7.10:reg_lifecycle_stage>>
_Why: 27002:7.10 — life cycle_

> _Standard text:_ Per-row lifecycle stage (in-use / in-transit / awaiting-disposal / disposed)

### Reg Issued Date

<<MUST item:A.7.10:reg_issued_date>>
_Why: Drift detection_

> _Standard text:_ Per-row issue date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Seen

<<SHOULD item:A.7.10:reg_last_seen>>
_Why: Loss detection_

> _Standard text:_ Per-row last-seen timestamp (drives stale-issue detection)
