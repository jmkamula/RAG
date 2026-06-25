---
leaf_id: req:A.5.27:lessons_program_review
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Lessons-Learned Program Review

> The lessons program creates value only if it closes the loop — actions actually get done, lessons reduce repeat incidents, and the patterns drive systemic improvements. The review captures the planned-interval check: action-closure rate, repeat-incident detection, training-impact evidence, feedback-loop effectiveness and resulting program adjustments

<!-- TABLE-COLUMNS leaf:req:A.5.27:lessons_program_review -->
<!-- column: item:A.5.27:rev_date -->
<!-- column: item:A.5.27:rev_reviewer -->
<!-- column: item:A.5.27:rev_closure_rate -->
<!-- column: item:A.5.27:rev_repeat -->
<!-- column: item:A.5.27:rev_training_impact -->
<!-- column: item:A.5.27:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.27:lessons_program_review -->
| Rev Date | Rev Reviewer | Rev Closure Rate | Rev Repeat | Rev Training Impact | Rev Actions |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.27:lessons_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.27:rev_date>>
_Why: 27002:5.27 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.5.27:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (program owner + InfoSec lead jointly)

### Rev Closure Rate

<<MUST item:A.5.27:rev_closure_rate>>
_Why: 27002:5.27a_

> _Standard text:_ Action-closure rate analysed (open / aged / closed) against targets

### Rev Repeat

<<MUST item:A.5.27:rev_repeat>>
_Why: 27002:5.27a,e_

> _Standard text:_ Repeat-incident analysis (lessons that should have prevented later incidents — did they?)

### Rev Training Impact

<<MUST item:A.5.27:rev_training_impact>>
_Why: 27002:5.27d_

> _Standard text:_ Training-impact evidence reviewed where lessons drove curriculum changes

### Rev Actions

<<MUST item:A.5.27:rev_actions>>
_Why: 27002:5.27_

> _Standard text:_ Action items captured for the program (e.g. tighten root-cause typing, expand pattern scope)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Benchmark

<<SHOULD item:A.5.27:rev_benchmark>>
_Why: Audit defensibility_

> _Standard text:_ External benchmark or industry-practice input considered

### Rev Next Date

<<SHOULD item:A.5.27:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
