---
leaf_id: req:A.5.22:program_meta_review
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Periodic Supplier Review Program Meta-Review

<<DOC_CONTROL>>

> The review program itself needs review — are we covering enough of the portfolio, is the cadence right, are findings being closed, is the program returning value? The meta-review evidences the periodic self-assessment of the program and the resulting adjustments

<!-- TABLE-COLUMNS leaf:req:A.5.22:program_meta_review -->
<!-- column: item:A.5.22:pgm_date -->
<!-- column: item:A.5.22:pgm_reviewer -->
<!-- column: item:A.5.22:pgm_coverage -->
<!-- column: item:A.5.22:pgm_closure -->
<!-- column: item:A.5.22:pgm_outcome -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document a yearly self-assessment of your supplier review program, ensuring you’re tracking coverage, cadence, issue closure, and overall value. It’s useful for showing your program is being regularly evaluated and improved.

## When to use it

Use this template once a year to record your review of the supplier review program itself, making sure it’s still effective and aligned with your needs. It applies to all environments where supplier oversight is required.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in thoughtfully.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.22:program_meta_review -->
| Pgm Date | Pgm Reviewer | Pgm Coverage | Pgm Closure | Pgm Outcome |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.22:program_meta_review -->

## Column guidance — what to fill in

### Pgm Date

<<MUST item:A.5.22:pgm_date>>
_Why: 27002:5.22 — periodic_

> _Standard text:_ Meta-review date within the planned interval

<<GUIDANCE>>

### Pgm Reviewer

<<MUST item:A.5.22:pgm_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (program owner + InfoSec lead jointly)

<<GUIDANCE>>

### Pgm Coverage

<<MUST item:A.5.22:pgm_coverage>>
_Why: Operational discipline_

> _Standard text:_ Coverage rate (fraction of supplier portfolio reviewed in period, by tier)

<<GUIDANCE>>

### Pgm Closure

<<MUST item:A.5.22:pgm_closure>>
_Why: Operational discipline_

> _Standard text:_ Findings-closure rate (open / aged / closed) across the portfolio

<<GUIDANCE>>

### Pgm Outcome

<<MUST item:A.5.22:pgm_outcome>>
_Why: 27002:5.22a,j_

> _Standard text:_ Cadence-adjustment decisions or scope-adjustment decisions (tighten / loosen / re-tier)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Pgm Benchmark

<<SHOULD item:A.5.22:pgm_benchmark>>
_Why: Audit defensibility_

> _Standard text:_ External benchmarking or industry-practice input considered

<<GUIDANCE>>

### Pgm Next Date

<<SHOULD item:A.5.22:pgm_next_date>>
_Why: Planning_

> _Standard text:_ Next planned meta-review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
