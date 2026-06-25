---
leaf_id: req:A.8.29:test_program_review
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Security Testing Program Review

> Periodic verification — test-coverage gaps, finding-pattern trending, pen-test outcomes feeding back (freshness=180; testing landscape evolves with threats)

<!-- TABLE-COLUMNS leaf:req:A.8.29:test_program_review -->
<!-- column: item:A.8.29:rev_date -->
<!-- column: item:A.8.29:rev_reviewer -->
<!-- column: item:A.8.29:rev_coverage_gaps -->
<!-- column: item:A.8.29:rev_pattern_trending -->
<!-- column: item:A.8.29:rev_pen_test_feedback -->
<!-- column: item:A.8.29:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.29:test_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Gaps | Rev Pattern Trending | Rev Pen Test Feedback | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.29:test_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.29:rev_date>>
_Why: 27002:8.29 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.29:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Security Engineering + Engineering leads)

### Rev Coverage Gaps

<<MUST item:A.8.29:rev_coverage_gaps>>
_Why: 27002:8.29 — coverage_

> _Standard text:_ Test-coverage gap check vs applicable scope

### Rev Pattern Trending

<<MUST item:A.8.29:rev_pattern_trending>>
_Why: Continuous improvement_

> _Standard text:_ Finding-pattern trending (recurring patterns → SDLC / training / tooling action)

### Rev Pen Test Feedback

<<MUST item:A.8.29:rev_pen_test_feedback>>
_Why: Closes the loop_

> _Standard text:_ Pen-test outcomes feeding back into procedure / scope / training

### Rev Findings Update

<<MUST item:A.8.29:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope / tooling

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.29:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
