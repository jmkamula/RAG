---
leaf_id: req:A.8.5:authentication_program_review
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Authentication Program Review

> Periodic verification that authentication baseline still matches threat landscape, exception inventory is current, and the log shows expected hygiene (freshness=180; auth attack patterns evolve fast)

<!-- TABLE-COLUMNS leaf:req:A.8.5:authentication_program_review -->
<!-- column: item:A.8.5:rev_date -->
<!-- column: item:A.8.5:rev_reviewer -->
<!-- column: item:A.8.5:rev_threat_landscape -->
<!-- column: item:A.8.5:rev_exception_inventory -->
<!-- column: item:A.8.5:rev_anomaly_outcomes -->
<!-- column: item:A.8.5:rev_baseline_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.5:authentication_program_review -->
| Rev Date | Rev Reviewer | Rev Threat Landscape | Rev Exception Inventory | Rev Anomaly Outcomes | Rev Baseline Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.5:authentication_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.5:rev_date>>
_Why: 27002:8.5 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IAM lead + InfoSec lead jointly)

### Rev Threat Landscape

<<MUST item:A.8.5:rev_threat_landscape>>
_Why: 27002:8.5 — secure (currency)_

> _Standard text:_ Threat-landscape review (new attack patterns since last review — feed from threat intel A.5.7)

### Rev Exception Inventory

<<MUST item:A.8.5:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

### Rev Anomaly Outcomes

<<MUST item:A.8.5:rev_anomaly_outcomes>>
_Why: Detection effectiveness_

> _Standard text:_ Anomaly-detection outcomes reviewed (true-positive rate, missed-detection postmortems)

### Rev Baseline Update

<<MUST item:A.8.5:rev_baseline_update>>
_Why: Closes the loop_

> _Standard text:_ Baseline / procedure updates published from findings

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
