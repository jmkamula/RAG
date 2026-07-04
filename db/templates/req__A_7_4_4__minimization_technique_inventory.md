---
leaf_id: req:A.7.4.4:minimization_technique_inventory
control_ref: A.7.4.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Minimization Technique Inventory

> Per-processing-activity row — the applied minimisation technique + degree + rationale. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.4:minimization_technique_inventory -->
<!-- column: item:A.7.4.4:reg_activity_id -->
<!-- column: item:A.7.4.4:reg_objective -->
<!-- column: item:A.7.4.4:reg_technique -->
<!-- column: item:A.7.4.4:reg_implementation -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.4:minimization_technique_inventory -->
| Reg Activity Id | Reg Objective | Reg Technique | Reg Implementation |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.4:minimization_technique_inventory -->

## Column guidance — what to fill in

### Reg Activity Id

<<MUST item:A.7.4.4:reg_activity_id>>
_Why: Traceability_

> _Standard text:_ Processing activity identifier per row

### Reg Objective

<<MUST item:A.7.4.4:reg_objective>>
_Why: §7.4.4_

> _Standard text:_ Minimization objective per row (target identifiability level — identified / pseudonymised / anonymised)

### Reg Technique

<<MUST item:A.7.4.4:reg_technique>>
_Why: §7.4.4 — mechanisms_

> _Standard text:_ Technique per row (masking / generalisation / suppression / noise addition / k-anonymity / differential privacy / etc.)

### Reg Implementation

<<MUST item:A.7.4.4:reg_implementation>>
_Why: §7.4.4 — technical configurations_

> _Standard text:_ Implementation reference per row (code repo / config file / infrastructure component)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Effectiveness Test

<<SHOULD item:A.7.4.4:reg_effectiveness_test>>
_Why: Defensibility_

> _Standard text:_ Effectiveness assessment per row (re-identification risk estimate)
