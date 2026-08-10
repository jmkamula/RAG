---
leaf_id: req:B.8.4.1:temp_files_sweep_register
control_ref: B.8.4.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor Temp Files Sweep Register

<<DOC_CONTROL>>

> Per-sweep-run row — customer-service infrastructure sweep records. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.4.1:temp_files_sweep_register -->
<!-- column: item:B.8.4.1:reg_sweep_id -->
<!-- column: item:B.8.4.1:reg_system -->
<!-- column: item:B.8.4.1:reg_scan_date -->
<!-- column: item:B.8.4.1:reg_files_cleaned -->
<!-- column: item:B.8.4.1:reg_tenant_boundary_check -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of each sweep of temporary files in your customer-service systems, supporting privacy compliance and audit readiness.

## When to use it

Use this register whenever your operations match the specific criteria for processor temp file sweeps, and update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 50 to 75 minutes to complete all required sections for each sweep entry, depending on the amount of detail you need to provide.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.4.1:temp_files_sweep_register -->
| Reg Sweep Id | Reg System | Reg Scan Date | Reg Files Cleaned | Reg Tenant Boundary Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.4.1:temp_files_sweep_register -->

## Column guidance — what to fill in

### Reg Sweep Id

<<MUST item:B.8.4.1:reg_sweep_id>>
_Why: Audit trail_

> _Standard text:_ Unique sweep run identifier per row

<<GUIDANCE>>

### Reg System

<<MUST item:B.8.4.1:reg_system>>
_Why: Coverage_

> _Standard text:_ System / component per row

<<GUIDANCE>>

### Reg Scan Date

<<MUST item:B.8.4.1:reg_scan_date>>
_Why: Currency_

> _Standard text:_ Scan date per row

<<GUIDANCE>>

### Reg Files Cleaned

<<MUST item:B.8.4.1:reg_files_cleaned>>
_Why: Effectiveness_

> _Standard text:_ Files cleaned per row

<<GUIDANCE>>

### Reg Tenant Boundary Check

<<MUST item:B.8.4.1:reg_tenant_boundary_check>>
_Why: Multi-tenant discipline_

> _Standard text:_ Tenant-boundary integrity check per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Anomalies

<<SHOULD item:B.8.4.1:reg_anomalies>>
_Why: Drift detection_

> _Standard text:_ Anomalies per row (accumulation / undue retention)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
