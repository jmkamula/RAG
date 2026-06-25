---
leaf_id: req:A.8.32:change_register
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Change Register

> Per-change record — change id, target, risk tier, approval lineage, outcome, rollback-invoked flag. The continuous evidence stream

<!-- TABLE-COLUMNS leaf:req:A.8.32:change_register -->
<!-- column: item:A.8.32:reg_change_id -->
<!-- column: item:A.8.32:reg_target -->
<!-- column: item:A.8.32:reg_risk_tier -->
<!-- column: item:A.8.32:reg_approval_lineage -->
<!-- column: item:A.8.32:reg_outcome -->
<!-- column: item:A.8.32:reg_emergency_flag -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.32:change_register -->
| Reg Change Id | Reg Target | Reg Risk Tier | Reg Approval Lineage | Reg Outcome | Reg Emergency Flag |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.32:change_register -->

## Column guidance — what to fill in

### Reg Change Id

<<MUST item:A.8.32:reg_change_id>>
_Why: Auditability_

> _Standard text:_ Per-change unique identifier

### Reg Target

<<MUST item:A.8.32:reg_target>>
_Why: Cross-control coherence_

> _Standard text:_ Per-change target (system / config / data; cross-link to A.5.9 asset register)

### Reg Risk Tier

<<MUST item:A.8.32:reg_risk_tier>>
_Why: 27002:8.32 — change management_

> _Standard text:_ Per-change risk tier (drives approval path applied)

### Reg Approval Lineage

<<MUST item:A.8.32:reg_approval_lineage>>
_Why: Accountability_

> _Standard text:_ Per-change approval lineage (approver(s) + timestamp)

### Reg Outcome

<<MUST item:A.8.32:reg_outcome>>
_Why: Continuous evidence_

> _Standard text:_ Per-change outcome (success / partial / rolled-back / failed)

### Reg Emergency Flag

<<MUST item:A.8.32:reg_emergency_flag>>
_Why: Operational reality_

> _Standard text:_ Per-change emergency flag + post-hoc-review reference where emergency

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Actor

<<SHOULD item:A.8.32:reg_actor>>
_Why: Accountability_

> _Standard text:_ Per-change actor (person or automated job)
