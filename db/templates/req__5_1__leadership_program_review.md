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

<<DOC_CONTROL>>

> Annual verification that leadership commitment is being visibly demonstrated — directive signed and current, framework being followed, reaffirmations on cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:5.1:leadership_program_review -->
<!-- column: item:5.1:rev_date -->
<!-- column: item:5.1:rev_reviewer -->
<!-- column: item:5.1:rev_directive_currency -->
<!-- column: item:5.1:rev_framework_adherence -->
<!-- column: item:5.1:rev_reaffirmation_completeness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review your organization's leadership commitment to information security, ensuring all key actions and directives are up to date and visibly supported by management.

## When to use it

Use this template whenever you need to confirm that leadership involvement in your security program is current and effective, typically once a year as part of your ongoing compliance activities.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in with relevant details.

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

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:5.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + non-executive director if available)

<<GUIDANCE>>

### Rev Directive Currency

<<MUST item:5.1:rev_directive_currency>>
_Why: Drift detection_

> _Standard text:_ Directive currency check — signed by current top management

<<GUIDANCE>>

### Rev Framework Adherence

<<MUST item:5.1:rev_framework_adherence>>
_Why: Cross-leaf coherence_

> _Standard text:_ Framework adherence check — board cadence happened, sponsor activities completed

<<GUIDANCE>>

### Rev Reaffirmation Completeness

<<MUST item:5.1:rev_reaffirmation_completeness>>
_Why: Cross-leaf coherence_

> _Standard text:_ Reaffirmation record completeness — required reaffirmations all present

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:5.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
