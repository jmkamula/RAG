---
leaf_id: req:10.2:nc_program_review
control_ref: 10.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# NC/CA Program Review

<<DOC_CONTROL>>

> Annual verification that NCs are flowing through the procedure, root cause is being done properly (not blamed-on-individual), effectiveness checks actually prevent recurrence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:10.2:nc_program_review -->
<!-- column: item:10.2:rev_date -->
<!-- column: item:10.2:rev_reviewer -->
<!-- column: item:10.2:rev_closure_progress -->
<!-- column: item:10.2:rev_root_cause_quality -->
<!-- column: item:10.2:rev_recurrence_check -->
<!-- column: item:10.2:rev_isms_change_pattern -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of how nonconformities are managed, ensuring root causes are properly analyzed and that corrective actions are effective in preventing repeat issues.

## When to use it

Use this template once a year to record your review of nonconformity handling, as required for ISO 27001 compliance. It applies to all environments and should be refreshed every 12 months.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of nonconformities reviewed and the detail required for each section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:10.2:nc_program_review -->
| Rev Date | Rev Reviewer | Rev Closure Progress | Rev Root Cause Quality | Rev Recurrence Check | Rev Isms Change Pattern |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:10.2:nc_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:10.2:rev_date>>
_Why: Clause 10.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:10.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + lead auditor)

<<GUIDANCE>>

### Rev Closure Progress

<<MUST item:10.2:rev_closure_progress>>
_Why: Effectiveness_

> _Standard text:_ Closure-progress check — open NCs aging beyond expected closure time escalated

<<GUIDANCE>>

### Rev Root Cause Quality

<<MUST item:10.2:rev_root_cause_quality>>
_Why: Clause 10.2 b)_

> _Standard text:_ Root-cause-quality sample — sampled NCs reviewed for blame-free systemic analysis (not 'human error' as the only cause)

<<GUIDANCE>>

### Rev Recurrence Check

<<MUST item:10.2:rev_recurrence_check>>
_Why: Clause 10.2 d)_

> _Standard text:_ Recurrence check — closed NCs sampled for whether the same nature recurred (effectiveness failure signal)

<<GUIDANCE>>

### Rev Isms Change Pattern

<<MUST item:10.2:rev_isms_change_pattern>>
_Why: Clause 10.2 e)_

> _Standard text:_ ISMS-change pattern check — high-volume NC areas drove 6.3 ISMS changes where systemic causes warranted it

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:10.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
