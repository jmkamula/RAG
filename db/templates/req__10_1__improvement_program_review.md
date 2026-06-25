---
leaf_id: req:10.1:improvement_program_review
control_ref: 10.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Continual Improvement Program Review

> Annual verification that the procedure is generating actions, the register reflects all triggers, completed actions had effectiveness checks (freshness=365)

<!-- TABLE-COLUMNS leaf:req:10.1:improvement_program_review -->
<!-- column: item:10.1:rev_date -->
<!-- column: item:10.1:rev_reviewer -->
<!-- column: item:10.1:rev_signal_capture -->
<!-- column: item:10.1:rev_dimension_coverage -->
<!-- column: item:10.1:rev_closure_quality -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:10.1:improvement_program_review -->
| Rev Date | Rev Reviewer | Rev Signal Capture | Rev Dimension Coverage | Rev Closure Quality |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:10.1:improvement_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:10.1:rev_date>>
_Why: Clause 10.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:10.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + executive sponsor)

### Rev Signal Capture

<<MUST item:10.1:rev_signal_capture>>
_Why: Coverage_

> _Standard text:_ Signal-capture check — every in-scope trigger source produced at least one action OR explicit 'no opportunities this cycle' rationale

### Rev Dimension Coverage

<<MUST item:10.1:rev_dimension_coverage>>
_Why: Clause 10.1 — three dimensions_

> _Standard text:_ Dimension coverage — improvements span suitability AND adequacy AND effectiveness (not just one)

### Rev Closure Quality

<<MUST item:10.1:rev_closure_quality>>
_Why: Effectiveness_

> _Standard text:_ Closure-quality check — closed actions have effectiveness assessment, not just 'marked complete'

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:10.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
