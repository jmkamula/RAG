---
leaf_id: req:B.8.2.1:program_review
control_ref: B.8.2.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Customer Agreement Program Review

<<DOC_CONTROL>>

> Annual verification — every in-scope customer has an executed processing agreement covering the required assistance obligations (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.1:program_review -->
<!-- column: item:B.8.2.1:rev_date -->
<!-- column: item:B.8.2.1:rev_reviewer -->
<!-- column: item:B.8.2.1:rev_coverage_check -->
<!-- column: item:B.8.2.1:rev_gaps_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of which customers have signed processing agreements that meet privacy requirements, making it easier to demonstrate compliance with ISO 27701.

## When to use it

Use this review record when your organization handles customer data and needs to confirm, once a year, that all relevant customers have up-to-date agreements in place.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on how many customers you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.1:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Gaps Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.2.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Legal + DPO + Sales Ops)

<<GUIDANCE>>

### Rev Coverage Check

<<MUST item:B.8.2.1:rev_coverage_check>>
_Why: §8.2.1 — where relevant_

> _Standard text:_ Coverage check — every in-scope customer has an executed agreement on file

<<GUIDANCE>>

### Rev Gaps Audit

<<MUST item:B.8.2.1:rev_gaps_audit>>
_Why: §8.2.1 — assistance obligations_

> _Standard text:_ Gaps audit — sampled agreements checked for Art.28.3.e-h assistance coverage

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
