---
leaf_id: req:A.8.12:dlp_program_review
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic DLP Program Review

> Periodic verification — ruleset currency, channel coverage gaps, true/false-positive trending, exception inventory (freshness=180; data-loss attack patterns evolve fast)

<!-- TABLE-COLUMNS leaf:req:A.8.12:dlp_program_review -->
<!-- column: item:A.8.12:rev_date -->
<!-- column: item:A.8.12:rev_reviewer -->
<!-- column: item:A.8.12:rev_coverage_gaps -->
<!-- column: item:A.8.12:rev_tp_rate -->
<!-- column: item:A.8.12:rev_exception_inventory -->
<!-- column: item:A.8.12:rev_baseline_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.12:dlp_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Gaps | Rev Tp Rate | Rev Exception Inventory | Rev Baseline Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.12:dlp_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.12:rev_date>>
_Why: 27002:8.12 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.12:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DLP lead + Data Protection + InfoSec)

### Rev Coverage Gaps

<<MUST item:A.8.12:rev_coverage_gaps>>
_Why: 27002:8.12 — measures_

> _Standard text:_ Channel-coverage gap check (new channel / new platform missing)

### Rev Tp Rate

<<MUST item:A.8.12:rev_tp_rate>>
_Why: Detection effectiveness_

> _Standard text:_ True-positive rate trending (detection effectiveness)

### Rev Exception Inventory

<<MUST item:A.8.12:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

### Rev Baseline Update

<<MUST item:A.8.12:rev_baseline_update>>
_Why: Closes the loop_

> _Standard text:_ Baseline / ruleset / procedure updates published from findings

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.12:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
