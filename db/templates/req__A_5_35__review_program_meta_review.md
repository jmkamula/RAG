---
leaf_id: req:A.5.35:review_program_meta_review
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Independent Review Program Meta-Review

> The review program itself needs review — are we picking reviewers that stay genuinely independent, is the cadence right, are findings closing, do reviews surface real issues or have they become rubber-stamps? The meta-review evidences periodic self-assessment of the review program and resulting adjustments

<!-- TABLE-COLUMNS leaf:req:A.5.35:review_program_meta_review -->
<!-- column: item:A.5.35:pgm_date -->
<!-- column: item:A.5.35:pgm_reviewer -->
<!-- column: item:A.5.35:pgm_independence_check -->
<!-- column: item:A.5.35:pgm_coverage -->
<!-- column: item:A.5.35:pgm_closure -->
<!-- column: item:A.5.35:pgm_outcome -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.35:review_program_meta_review -->
| Pgm Date | Pgm Reviewer | Pgm Independence Check | Pgm Coverage | Pgm Closure | Pgm Outcome |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.35:review_program_meta_review -->

## Column guidance — what to fill in

### Pgm Date

<<MUST item:A.5.35:pgm_date>>
_Why: 27002:5.35 — periodic_

> _Standard text:_ Meta-review date within the planned interval

### Pgm Reviewer

<<MUST item:A.5.35:pgm_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (program owner + InfoSec lead jointly + audit committee chair where applicable)

### Pgm Independence Check

<<MUST item:A.5.35:pgm_independence_check>>
_Why: 27002:5.35 — reviewed independently_

> _Standard text:_ Independence-discipline check — did the actual reviewers meet the criteria? rotation worked? any reviewer reviewing their own area?

### Pgm Coverage

<<MUST item:A.5.35:pgm_coverage>>
_Why: 27002:5.35 — planned intervals_

> _Standard text:_ Coverage check — did the schedule actually run? all planned scope areas reviewed?

### Pgm Closure

<<MUST item:A.5.35:pgm_closure>>
_Why: Operational discipline_

> _Standard text:_ Findings-closure rate across the program (open / aged / closed)

### Pgm Outcome

<<MUST item:A.5.35:pgm_outcome>>
_Why: 27002:5.35 — adjustments_

> _Standard text:_ Cadence-adjustment or scope-adjustment decisions (tighten / loosen / re-tier / change reviewer pool)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Pgm Benchmark

<<SHOULD item:A.5.35:pgm_benchmark>>
_Why: Audit defensibility_

> _Standard text:_ External benchmarking or industry-practice input considered

### Pgm Next Date

<<SHOULD item:A.5.35:pgm_next_date>>
_Why: Planning_

> _Standard text:_ Next planned meta-review date stated
