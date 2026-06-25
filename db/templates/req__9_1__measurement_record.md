---
leaf_id: req:9.1:measurement_record
control_ref: 9.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# ISMS Measurement Record

> The live measurement output — per-metric values captured over time, analysed against thresholds, fed into 9.3 management review. Distinct from the procedure: the procedure is the plan, this is the data. Quarterly refresh (freshness=90 — measurement tempo)

<!-- TABLE-COLUMNS leaf:req:9.1:measurement_record -->
<!-- column: item:9.1:rec_metric_id -->
<!-- column: item:9.1:rec_value -->
<!-- column: item:9.1:rec_date -->
<!-- column: item:9.1:rec_threshold -->
<!-- column: item:9.1:rec_status -->
<!-- column: item:9.1:rec_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:9.1:measurement_record -->
| Rec Metric Id | Rec Value | Rec Date | Rec Threshold | Rec Status | Rec Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:9.1:measurement_record -->

## Column guidance — what to fill in

### Rec Metric Id

<<MUST item:9.1:rec_metric_id>>
_Why: Cross-leaf coherence_

> _Standard text:_ Metric identifier per row (matches procedure's metric catalog)

### Rec Value

<<MUST item:9.1:rec_value>>
_Why: Clause 9.1 — measurement_

> _Standard text:_ Per-row measured value

### Rec Date

<<MUST item:9.1:rec_date>>
_Why: Currency_

> _Standard text:_ Per-row measurement date

### Rec Threshold

<<MUST item:9.1:rec_threshold>>
_Why: Clause 9.1 — evaluation_

> _Standard text:_ Per-row threshold / target value applied

### Rec Status

<<MUST item:9.1:rec_status>>
_Why: Clause 9.1 — analysis_

> _Standard text:_ Per-row status (above-target / on-target / below-target / breach)

### Rec Owner

<<MUST item:9.1:rec_owner>>
_Why: Accountability_

> _Standard text:_ Per-row metric owner

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rec Trend

<<SHOULD item:9.1:rec_trend>>
_Why: Trend visibility_

> _Standard text:_ Per-row trend annotation (rising / stable / falling)
