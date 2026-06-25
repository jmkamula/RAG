---
leaf_id: req:A.8.9:configuration_program_review
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Configuration Program Review

> Annual review — baseline currency vs vendor/threat updates, deviation inventory, drift-detection effectiveness (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.9:configuration_program_review -->
<!-- column: item:A.8.9:rev_date -->
<!-- column: item:A.8.9:rev_reviewer -->
<!-- column: item:A.8.9:rev_baseline_currency -->
<!-- column: item:A.8.9:rev_deviation_inventory -->
<!-- column: item:A.8.9:rev_drift_effectiveness -->
<!-- column: item:A.8.9:rev_baselines_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.9:configuration_program_review -->
| Rev Date | Rev Reviewer | Rev Baseline Currency | Rev Deviation Inventory | Rev Drift Effectiveness | Rev Baselines Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.9:configuration_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.9:rev_date>>
_Why: 27002:8.9 — reviewed_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure leads + InfoSec)

### Rev Baseline Currency

<<MUST item:A.8.9:rev_baseline_currency>>
_Why: 27002:8.9 — reviewed_

> _Standard text:_ Baseline-vs-vendor-current check (CIS / vendor / NIST version drift)

### Rev Deviation Inventory

<<MUST item:A.8.9:rev_deviation_inventory>>
_Why: Drift prevention_

> _Standard text:_ Deviation inventory re-confirmed / retired

### Rev Drift Effectiveness

<<MUST item:A.8.9:rev_drift_effectiveness>>
_Why: Detection effectiveness_

> _Standard text:_ Drift-detection effectiveness review (catch rate, MTTR)

### Rev Baselines Update

<<MUST item:A.8.9:rev_baselines_update>>
_Why: Closes the loop_

> _Standard text:_ Updated baselines published from findings

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
