---
leaf_id: req:A.8.33:test_dataset_register
control_ref: A.8.33
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Test Dataset Register

> Per-dataset catalogue — dataset id, source, current treatment (synthetic / masked / live-PII-banned), location, last-refresh, retention status

<!-- TABLE-COLUMNS leaf:req:A.8.33:test_dataset_register -->
<!-- column: item:A.8.33:reg_dataset_id -->
<!-- column: item:A.8.33:reg_source -->
<!-- column: item:A.8.33:reg_treatment -->
<!-- column: item:A.8.33:reg_location -->
<!-- column: item:A.8.33:reg_last_refresh -->
<!-- column: item:A.8.33:reg_retention_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.33:test_dataset_register -->
| Reg Dataset Id | Reg Source | Reg Treatment | Reg Location | Reg Last Refresh | Reg Retention Status |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.33:test_dataset_register -->

## Column guidance — what to fill in

### Reg Dataset Id

<<MUST item:A.8.33:reg_dataset_id>>
_Why: Identification_

> _Standard text:_ Per-row dataset identifier

### Reg Source

<<MUST item:A.8.33:reg_source>>
_Why: 27002:8.33 — selected_

> _Standard text:_ Per-row source (synthetic-generator / production-snapshot / vendor-provided / contributed-by-user)

### Reg Treatment

<<MUST item:A.8.33:reg_treatment>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row treatment applied (synthetic / static-masked / dynamic-masked / pseudonymised)

### Reg Location

<<MUST item:A.8.33:reg_location>>
_Why: 27002:8.33 — managed_

> _Standard text:_ Per-row storage location + access-control reference

### Reg Last Refresh

<<MUST item:A.8.33:reg_last_refresh>>
_Why: Drift detection_

> _Standard text:_ Per-row last refresh timestamp (drives stale-test-data detection)

### Reg Retention Status

<<MUST item:A.8.33:reg_retention_status>>
_Why: 27002:8.33 — managed_

> _Standard text:_ Per-row retention status (active / scheduled-for-deletion / archived)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.33:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row named owner
