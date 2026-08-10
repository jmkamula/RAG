---
leaf_id: req:A.6.3:awareness_programme_review
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Awareness Programme Review

<<DOC_CONTROL>>

> Periodic verification that the curriculum still matches current policies, the completion register has no gaps, effectiveness metrics are trending right, and awareness mechanisms are being executed. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.3:awareness_programme_review -->
<!-- column: item:A.6.3:rev_date -->
<!-- column: item:A.6.3:rev_reviewer -->
<!-- column: item:A.6.3:rev_completion_rate -->
<!-- column: item:A.6.3:rev_effectiveness -->
<!-- column: item:A.6.3:rev_curriculum_check -->
<!-- column: item:A.6.3:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your awareness programme’s effectiveness, making sure your training content and processes stay up to date with company policies and compliance requirements.

## When to use it

Use this review record once a year to confirm your awareness programme is current, effective, and fully documented—this applies to every environment, regardless of changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how many awareness activities and records you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.3:awareness_programme_review -->
| Rev Date | Rev Reviewer | Rev Completion Rate | Rev Effectiveness | Rev Curriculum Check | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.3:awareness_programme_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.3:rev_date>>
_Why: 27002:6.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.6.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Security Awareness Lead + InfoSec lead jointly)

<<GUIDANCE>>

### Rev Completion Rate

<<MUST item:A.6.3:rev_completion_rate>>
_Why: 27002:6.3 — completeness_

> _Standard text:_ Completion rate analysis (overall % current; per-audience-segment % current; aged-overdue list)

<<GUIDANCE>>

### Rev Effectiveness

<<MUST item:A.6.3:rev_effectiveness>>
_Why: 27002:6.3 — effectiveness_

> _Standard text:_ Effectiveness analysis (quiz pass-rate trend, phishing-simulation click-rate trend, reporting-rate trend per A.6.8)

<<GUIDANCE>>

### Rev Curriculum Check

<<MUST item:A.6.3:rev_curriculum_check>>
_Why: 27002:6.3 — current_

> _Standard text:_ Curriculum currency check (referenced policies still align with the training content; new topics added per scope changes)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.6.3:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the curriculum / register / scope with reference to this review

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.3:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (major incident exposing awareness gap, new compliance regime, major tech adoption)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.6.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
