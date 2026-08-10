---
leaf_id: req:A.7.5.3:program_review
control_ref: A.7.5.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Transfer Records Program Review

<<DOC_CONTROL>>

> Annual verification — transfer events captured, cooperation channels functional, minimisation principle applied (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.5.3:program_review -->
<!-- column: item:A.7.5.3:rev_date -->
<!-- column: item:A.7.5.3:rev_reviewer -->
<!-- column: item:A.7.5.3:rev_completeness -->
<!-- column: item:A.7.5.3:rev_cooperation_test -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and document how transfer events are recorded, how well your cooperation processes work, and whether you’re minimizing data retention in line with privacy standards.

## When to use it

Use this review record if your organization handles data transfers and needs to check these processes annually, especially when your activities match certain privacy-related triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of transfer events you need to document in the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.3:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Cooperation Test |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.5.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.5.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Data Ops)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.7.5.3:rev_completeness>>
_Why: §7.5.3 — record transfers_

> _Standard text:_ Completeness check — actual transfer events reconciled against log

<<GUIDANCE>>

### Rev Cooperation Test

<<MUST item:A.7.5.3:rev_cooperation_test>>
_Why: §7.5.3 — cooperation_

> _Standard text:_ Cooperation channel test — sampled third parties re-contactable for subject-rights follow-up

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.5.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
