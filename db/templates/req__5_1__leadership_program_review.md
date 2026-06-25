---
leaf_id: req:5.1:leadership_program_review
control_ref: 5.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Leadership Program Review

> Annual verification that leadership commitment is being visibly demonstrated — directive signed and current, framework being followed, reaffirmations on cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:5.1:leadership_program_review -->
<!-- column: item:5.1:rev_date -->
<!-- column: item:5.1:rev_reviewer -->
<!-- column: item:5.1:rev_directive_currency -->
<!-- column: item:5.1:rev_framework_adherence -->
<!-- column: item:5.1:rev_reaffirmation_completeness -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.1:leadership_program_review -->
| Rev Date | Rev Reviewer | Rev Directive Currency | Rev Framework Adherence | Rev Reaffirmation Completeness |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.1:leadership_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:5.1:rev_date>>
_Why: Clause 5.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:5.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + non-executive director if available)

### Rev Directive Currency

<<MUST item:5.1:rev_directive_currency>>
_Why: Drift detection_

> _Standard text:_ Directive currency check — signed by current top management

### Rev Framework Adherence

<<MUST item:5.1:rev_framework_adherence>>
_Why: Cross-leaf coherence_

> _Standard text:_ Framework adherence check — board cadence happened, sponsor activities completed

### Rev Reaffirmation Completeness

<<MUST item:5.1:rev_reaffirmation_completeness>>
_Why: Cross-leaf coherence_

> _Standard text:_ Reaffirmation record completeness — required reaffirmations all present

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:5.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
