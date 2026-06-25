---
leaf_id: req:6.2:security_objectives_register
control_ref: 6.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Information Security Objectives Register

> Clause 6.2 requires information security objectives to be established at relevant functions and levels. The register is the canonical artefact — every objective with owner, KPI, target date, progress. Sibling leaves: objective-setting methodology, applicable functions scope, program review. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.2:security_objectives_register -->
<!-- column: item:6.2:objectives_stated -->
<!-- column: item:6.2:consistent_with_policy -->
<!-- column: item:6.2:measurable -->
<!-- column: item:6.2:owner -->
<!-- column: item:6.2:target_date -->
<!-- column: item:6.2:progress_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.2:security_objectives_register -->
| Objectives Stated | Consistent With Policy | Measurable | Owner | Target Date | Progress Status |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.2:security_objectives_register -->

## Column guidance — what to fill in

### Objectives Stated

<<MUST item:6.2:objectives_stated>>
_Why: Clause 6.2 — established at relevant functions and levels_

> _Standard text:_ Objectives stated at relevant functions and levels

### Consistent With Policy

<<MUST item:6.2:consistent_with_policy>>
_Why: Clause 6.2 a)_

> _Standard text:_ Per-objective consistency with the InfoSec policy (5.2) flagged

### Measurable

<<MUST item:6.2:measurable>>
_Why: Clause 6.2 b)_

> _Standard text:_ Per-objective KPI defined where practicable

### Owner

<<MUST item:6.2:owner>>
_Why: Accountability_

> _Standard text:_ Per-objective owner identified

### Target Date

<<MUST item:6.2:target_date>>
_Why: Concrete commitment_

> _Standard text:_ Per-objective target date stated

### Progress Status

<<MUST item:6.2:progress_status>>
_Why: Tracking_

> _Standard text:_ Per-objective progress status (on-track / at-risk / off-track / met)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Kpi Dashboard

<<SHOULD item:6.2:kpi_dashboard>>
_Why: Visibility_

> _Standard text:_ KPI dashboard linked
