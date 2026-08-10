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

<<DOC_CONTROL>>

> Per-processing-activity row — the applied minimisation technique + degree + rationale. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.4:minimization_technique_inventory -->
<!-- column: item:A.7.4.4:reg_activity_id -->
<!-- column: item:A.7.4.4:reg_objective -->
<!-- column: item:A.7.4.4:reg_technique -->
<!-- column: item:A.7.4.4:reg_implementation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of the data minimization techniques you use for each processing activity, along with the reasons and degree of minimization. It provides a clear, organized record for privacy compliance.

## When to use it

Use this register when your activities match certain privacy triggers, and update it about once a year to ensure your information stays current and compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each processing activity you document. Completing the register from scratch may take a few hours, depending on the number of activities you need to cover.

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

<<GUIDANCE>>

### Reg Objective

<<MUST item:A.7.4.4:reg_objective>>
_Why: §7.4.4_

> _Standard text:_ Minimization objective per row (target identifiability level — identified / pseudonymised / anonymised)

<<GUIDANCE>>

### Reg Technique

<<MUST item:A.7.4.4:reg_technique>>
_Why: §7.4.4 — mechanisms_

> _Standard text:_ Technique per row (masking / generalisation / suppression / noise addition / k-anonymity / differential privacy / etc.)

<<GUIDANCE>>

### Reg Implementation

<<MUST item:A.7.4.4:reg_implementation>>
_Why: §7.4.4 — technical configurations_

> _Standard text:_ Implementation reference per row (code repo / config file / infrastructure component)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Effectiveness Test

<<SHOULD item:A.7.4.4:reg_effectiveness_test>>
_Why: Defensibility_

> _Standard text:_ Effectiveness assessment per row (re-identification risk estimate)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
