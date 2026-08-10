---
leaf_id: req:8.2:operational_assessment_program_review
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Operational Assessment Program Review

<<DOC_CONTROL>>

> Annual verification that planned assessments happened, significant-change triggers fired when they should have, results inform the treatment plan (freshness=365)

<!-- TABLE-COLUMNS leaf:req:8.2:operational_assessment_program_review -->
<!-- column: item:8.2:rev_date -->
<!-- column: item:8.2:rev_reviewer -->
<!-- column: item:8.2:rev_cadence_met -->
<!-- column: item:8.2:rev_triggers_fired -->
<!-- column: item:8.2:rev_treatment_handoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your annual operational assessments, making sure all planned reviews happened and any major changes were properly addressed. It also ensures your assessment results are used to update your treatment plans.

## When to use it

Use this template once a year to review your operational assessment program, especially after any significant changes in your environment. It's designed to be relevant for all organizations, every year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how many assessments and changes you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.2:operational_assessment_program_review -->
| Rev Date | Rev Reviewer | Rev Cadence Met | Rev Triggers Fired | Rev Treatment Handoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.2:operational_assessment_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:8.2:rev_date>>
_Why: Clause 8.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:8.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Risk Manager + ISMS Manager)

<<GUIDANCE>>

### Rev Cadence Met

<<MUST item:8.2:rev_cadence_met>>
_Why: Clause 8.2 — planned intervals_

> _Standard text:_ Cadence-met check — every scheduled assessment for each tier happened

<<GUIDANCE>>

### Rev Triggers Fired

<<MUST item:8.2:rev_triggers_fired>>
_Why: Clause 8.2 — significant changes_

> _Standard text:_ Trigger-firing sweep — significant changes during the year that should have triggered ad-hoc assessment all did

<<GUIDANCE>>

### Rev Treatment Handoff

<<MUST item:8.2:rev_treatment_handoff>>
_Why: Cross-clause coherence_

> _Standard text:_ Treatment handoff — every new risk found flows to 6.1.3 / 8.3 treatment

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:8.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
