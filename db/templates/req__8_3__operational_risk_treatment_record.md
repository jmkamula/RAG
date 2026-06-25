---
leaf_id: req:8.3:operational_risk_treatment_record
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: risk_treatment_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Operational Risk Treatment Records

> Clause 8.3 requires the organisation to implement the 6.1.3 treatment plan and retain documented information of results. Per-treatment-item records are the canonical artefact. Sibling leaves: execution procedure, applicable plan-items scope, program review. Operational freshness (180d)

<!-- TABLE-COLUMNS leaf:req:8.3:operational_risk_treatment_record -->
<!-- column: item:8.3:plan_implemented -->
<!-- column: item:8.3:implementation_status -->
<!-- column: item:8.3:residual_risk -->
<!-- column: item:8.3:retention -->
<!-- column: item:8.3:per_item_owner -->
<!-- column: item:8.3:per_item_target_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.3:operational_risk_treatment_record -->
| Plan Implemented | Implementation Status | Residual Risk | Retention | Per Item Owner | Per Item Target Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.3:operational_risk_treatment_record -->

## Column guidance — what to fill in

### Plan Implemented

<<MUST item:8.3:plan_implemented>>
_Why: Clause 8.3 — implement the information security risk treatment plan_

> _Standard text:_ Treatment plan from 6.1.3 being implemented (status per item)

### Implementation Status

<<MUST item:8.3:implementation_status>>
_Why: Clause 8.3 — implementation_

> _Standard text:_ Implementation status per treatment item (planned, in-progress, complete, deferred)

### Residual Risk

<<MUST item:8.3:residual_risk>>
_Why: Clause 8.3 — results_

> _Standard text:_ Residual risk recorded after treatment

### Retention

<<MUST item:8.3:retention>>
_Why: Clause 8.3 — retain documented information of the results_

> _Standard text:_ Documented information of results retained

### Per Item Owner

<<MUST item:8.3:per_item_owner>>
_Why: Accountability_

> _Standard text:_ Per-treatment-item owner identified

### Per Item Target Date

<<MUST item:8.3:per_item_target_date>>
_Why: Tracking_

> _Standard text:_ Per-treatment-item target completion date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Soa Link

<<SHOULD item:8.3:soa_link>>
_Why: Audit traceability_

> _Standard text:_ Link to Statement of Applicability for control selection rationale
