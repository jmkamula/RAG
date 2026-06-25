---
leaf_id: req:A.8.27:architecture_register
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Reference Architecture Register

> Per-pattern catalogue — pattern id, applicable context, security principles embedded, last-review date

<!-- TABLE-COLUMNS leaf:req:A.8.27:architecture_register -->
<!-- column: item:A.8.27:reg_pattern_id -->
<!-- column: item:A.8.27:reg_context -->
<!-- column: item:A.8.27:reg_principles_embedded -->
<!-- column: item:A.8.27:reg_owner -->
<!-- column: item:A.8.27:reg_last_reviewed -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.27:architecture_register -->
| Reg Pattern Id | Reg Context | Reg Principles Embedded | Reg Owner | Reg Last Reviewed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.27:architecture_register -->

## Column guidance — what to fill in

### Reg Pattern Id

<<MUST item:A.8.27:reg_pattern_id>>
_Why: Identification_

> _Standard text:_ Per-pattern unique identifier

### Reg Context

<<MUST item:A.8.27:reg_context>>
_Why: 27002:8.27 — applied_

> _Standard text:_ Per-pattern applicable context (when to use this pattern)

### Reg Principles Embedded

<<MUST item:A.8.27:reg_principles_embedded>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-pattern principles embedded (mapping back to policy's principle set)

### Reg Owner

<<MUST item:A.8.27:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-pattern named owner

### Reg Last Reviewed

<<MUST item:A.8.27:reg_last_reviewed>>
_Why: Drift detection_

> _Standard text:_ Per-pattern last-review date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Usage Count

<<SHOULD item:A.8.27:reg_usage_count>>
_Why: Operational visibility_

> _Standard text:_ Per-pattern usage-count (how many projects adopted it — drives 'is this pattern actually used' signal)
