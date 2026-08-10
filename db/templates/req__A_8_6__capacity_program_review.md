---
leaf_id: req:A.8.6:capacity_program_review
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Capacity Program Review

<<DOC_CONTROL>>

> Annual verification that the capacity baseline still matches demand, forecasts are accurate, and the log shows expected hygiene (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.6:capacity_program_review -->
<!-- column: item:A.8.6:rev_date -->
<!-- column: item:A.8.6:rev_reviewer -->
<!-- column: item:A.8.6:rev_forecast_accuracy -->
<!-- column: item:A.8.6:rev_breach_patterns -->
<!-- column: item:A.8.6:rev_baseline_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of whether your capacity planning still matches your organization's needs and ensures your forecasts and records are up to date.

## When to use it

Use this review record once a year to confirm your capacity baseline, forecasts, and logs are still accurate and relevant for your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many updates or changes you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.6:capacity_program_review -->
| Rev Date | Rev Reviewer | Rev Forecast Accuracy | Rev Breach Patterns | Rev Baseline Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.6:capacity_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.6:rev_date>>
_Why: 27002:8.6 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + Finance + Engineering leadership)

<<GUIDANCE>>

### Rev Forecast Accuracy

<<MUST item:A.8.6:rev_forecast_accuracy>>
_Why: 27002:8.6 — expected_

> _Standard text:_ Forecast-vs-actual accuracy check across the review window

<<GUIDANCE>>

### Rev Breach Patterns

<<MUST item:A.8.6:rev_breach_patterns>>
_Why: Drift prevention_

> _Standard text:_ Breach-pattern review (recurring breaches → baseline re-calibration)

<<GUIDANCE>>

### Rev Baseline Update

<<MUST item:A.8.6:rev_baseline_update>>
_Why: Closes the loop_

> _Standard text:_ Baseline / threshold updates published from findings

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
