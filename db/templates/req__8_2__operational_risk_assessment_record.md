---
leaf_id: req:8.2:operational_risk_assessment_record
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: risk_assessment_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Operational Risk Assessment Records

> Clause 8.2 requires risk assessments to be performed at planned intervals or on significant change, using the criteria from 6.1.2. Per-assessment records are the canonical artefact. Sibling leaves: trigger procedure, applicable scope, program review. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:8.2:operational_risk_assessment_record -->
<!-- column: item:8.2:planned_interval -->
<!-- column: item:8.2:significant_change -->
<!-- column: item:8.2:last_assessment -->
<!-- column: item:8.2:criteria_applied -->
<!-- column: item:8.2:results_documented -->
<!-- column: item:8.2:owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.2:operational_risk_assessment_record -->
| Planned Interval | Significant Change | Last Assessment | Criteria Applied | Results Documented | Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.2:operational_risk_assessment_record -->

## Column guidance — what to fill in

### Planned Interval

<<MUST item:8.2:planned_interval>>
_Why: Clause 8.2 — planned intervals_

> _Standard text:_ Planned interval observed (typically annual or more frequent for higher-risk environments)

### Significant Change

<<MUST item:8.2:significant_change>>
_Why: Clause 8.2 — when significant changes are proposed or occur_

> _Standard text:_ Significant-change trigger for ad-hoc reassessments documented

### Last Assessment

<<MUST item:8.2:last_assessment>>
_Why: Currency_

> _Standard text:_ Last assessment date recorded

### Criteria Applied

<<MUST item:8.2:criteria_applied>>
_Why: Clause 8.2 — criteria established in 6.1.2 a_

> _Standard text:_ Criteria from 6.1.2 a) applied during assessment

### Results Documented

<<MUST item:8.2:results_documented>>
_Why: Clause 8.2 — retain documented information_

> _Standard text:_ Results documented and retained

### Owner

<<MUST item:8.2:owner>>
_Why: Accountability_

> _Standard text:_ Per-assessment owner (Risk Manager or function risk-owner)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comparison To Prior

<<SHOULD item:8.2:comparison_to_prior>>
_Why: Trend visibility_

> _Standard text:_ Comparison or movement from prior assessment
