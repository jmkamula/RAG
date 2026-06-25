---
leaf_id: req:A.8.3:access_matrix_register
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-System Access Matrix Register

> Catalogue of access matrices across systems — who can do what, per repository / dataset / application. Drives the recertification workflow

<!-- TABLE-COLUMNS leaf:req:A.8.3:access_matrix_register -->
<!-- column: item:A.8.3:per_system_matrix -->
<!-- column: item:A.8.3:reg_system_id -->
<!-- column: item:A.8.3:reg_owner -->
<!-- column: item:A.8.3:reg_last_recert -->
<!-- column: item:A.8.3:reg_classification -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.3:access_matrix_register -->
| Per System Matrix | Reg System Id | Reg Owner | Reg Last Recert | Reg Classification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.3:access_matrix_register -->

## Column guidance — what to fill in

### Per System Matrix

<<MUST item:A.8.3:per_system_matrix>>
_Why: 27002:8.3 — restricted_

> _Standard text:_ Access matrix per system / repository row (who, what permissions, on what resource)

### Reg System Id

<<MUST item:A.8.3:reg_system_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row system identifier (from asset register A.5.9)

### Reg Owner

<<MUST item:A.8.3:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row matrix owner (system owner accountable for accuracy)

### Reg Last Recert

<<MUST item:A.8.3:reg_last_recert>>
_Why: Drift detection_

> _Standard text:_ Per-row last recertification date (drives staleness detection)

### Reg Classification

<<MUST item:A.8.3:reg_classification>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row classification tier (drives enforcement strictness)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Exception Log

<<SHOULD item:A.8.3:reg_exception_log>>
_Why: Operational discipline_

> _Standard text:_ Exception log for temporary elevated access per row
