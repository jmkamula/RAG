---
leaf_id: req:6.1.1:planned_action_register
control_ref: 6.1.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# ISMS Planned Action Register

<<DOC_CONTROL>>

> The live output of the planning procedure — every action targeting a risk or opportunity with owner, due date, integration target. Distinct from the risk register (6.1.2) and the SoA (6.1.3): this tracks ISMS-level planning actions, not control implementations

<!-- TABLE-COLUMNS leaf:req:6.1.1:planned_action_register -->
<!-- column: item:6.1.1:reg_action_id -->
<!-- column: item:6.1.1:reg_driver -->
<!-- column: item:6.1.1:reg_type -->
<!-- column: item:6.1.1:reg_owner -->
<!-- column: item:6.1.1:reg_integration_target -->
<!-- column: item:6.1.1:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of every planned action related to risks or opportunities in your information security management system, showing who is responsible, due dates, and how each action fits into your wider program.

## When to use it

Use this register whenever you need to plan, assign, and monitor actions for your ISMS, especially when new risks or opportunities are identified. Update it whenever changes occur or new actions are needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the initial required elements, plus additional time for each action you add as your register grows.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.1.1:planned_action_register -->
| Reg Action Id | Reg Driver | Reg Type | Reg Owner | Reg Integration Target | Reg Status |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.1.1:planned_action_register -->

## Column guidance — what to fill in

### Reg Action Id

<<MUST item:6.1.1:reg_action_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique action identifier per row

<<GUIDANCE>>

### Reg Driver

<<MUST item:6.1.1:reg_driver>>
_Why: Cross-clause traceability_

> _Standard text:_ Per-row driver (4.1 issue id, 4.2 party requirement id, risk id, opportunity id)

<<GUIDANCE>>

### Reg Type

<<MUST item:6.1.1:reg_type>>
_Why: Clause 6.1.1 — risks AND opportunities_

> _Standard text:_ Per-row type (risk-addressing / opportunity-enhancing)

<<GUIDANCE>>

### Reg Owner

<<MUST item:6.1.1:reg_owner>>
_Why: Accountability_

> _Standard text:_ Owner per row

<<GUIDANCE>>

### Reg Integration Target

<<MUST item:6.1.1:reg_integration_target>>
_Why: Clause 6.1.1 — integrated into ISMS processes_

> _Standard text:_ Integration target per row (which ISMS process consumes this action)

<<GUIDANCE>>

### Reg Status

<<MUST item:6.1.1:reg_status>>
_Why: Tracking_

> _Standard text:_ Status per row (planned / in-progress / complete / deferred)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Effectiveness

<<SHOULD item:6.1.1:reg_effectiveness>>
_Why: Clause 6.1.1 — evaluate effectiveness_

> _Standard text:_ Per-row effectiveness evaluation captured on completion

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
