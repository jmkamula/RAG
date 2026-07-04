---
leaf_id: req:A.7.4.6:temp_files_sweep_register
control_ref: A.7.4.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Temp Files Sweep Register

> Per-sweep-run row — records of periodic sweeps + volumes cleaned. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.6:temp_files_sweep_register -->
<!-- column: item:A.7.4.6:reg_sweep_id -->
<!-- column: item:A.7.4.6:reg_system -->
<!-- column: item:A.7.4.6:reg_scan_date -->
<!-- column: item:A.7.4.6:reg_files_cleaned -->
<!-- column: item:A.7.4.6:reg_anomalies_flagged -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.6:temp_files_sweep_register -->
| Reg Sweep Id | Reg System | Reg Scan Date | Reg Files Cleaned | Reg Anomalies Flagged |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.6:temp_files_sweep_register -->

## Column guidance — what to fill in

### Reg Sweep Id

<<MUST item:A.7.4.6:reg_sweep_id>>
_Why: Audit trail_

> _Standard text:_ Unique sweep run identifier per row

### Reg System

<<MUST item:A.7.4.6:reg_system>>
_Why: Coverage_

> _Standard text:_ System / infrastructure component per row

### Reg Scan Date

<<MUST item:A.7.4.6:reg_scan_date>>
_Why: Currency_

> _Standard text:_ Scan date per row

### Reg Files Cleaned

<<MUST item:A.7.4.6:reg_files_cleaned>>
_Why: Effectiveness_

> _Standard text:_ Files cleaned + volume per row

### Reg Anomalies Flagged

<<MUST item:A.7.4.6:reg_anomalies_flagged>>
_Why: Drift detection_

> _Standard text:_ Anomalies flagged per row (unusual accumulation / temp files past retention)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Verified

<<SHOULD item:A.7.4.6:reg_last_verified>>
_Why: Effectiveness_

> _Standard text:_ Verification last-run date per row
