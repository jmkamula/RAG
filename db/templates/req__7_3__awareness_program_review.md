---
leaf_id: req:7.3:awareness_program_review
control_ref: 7.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Awareness Program Review

<<DOC_CONTROL>>

> Annual verification that the programme content reflects current policy, the audience is fully covered, completion rates are healthy, refresher cadence is being met (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.3:awareness_program_review -->
<!-- column: item:7.3:rev_date -->
<!-- column: item:7.3:rev_reviewer -->
<!-- column: item:7.3:rev_content_currency -->
<!-- column: item:7.3:rev_coverage -->
<!-- column: item:7.3:rev_refresher -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your awareness program, making sure it matches your current policies, covers everyone it should, and is being completed and refreshed as planned.

## When to use it

Use this review record once a year to confirm your awareness program is up to date and effective. It applies to all environments and should be refreshed annually.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes 10-15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.3:awareness_program_review -->
| Rev Date | Rev Reviewer | Rev Content Currency | Rev Coverage | Rev Refresher |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.3:awareness_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:7.3:rev_date>>
_Why: Clause 7.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:7.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR partner + ISMS Manager)

<<GUIDANCE>>

### Rev Content Currency

<<MUST item:7.3:rev_content_currency>>
_Why: Cross-clause coherence_

> _Standard text:_ Content currency check — material still reflects current 5.2 policy

<<GUIDANCE>>

### Rev Coverage

<<MUST item:7.3:rev_coverage>>
_Why: Effectiveness_

> _Standard text:_ Coverage check — register completion rate against the in-scope audience

<<GUIDANCE>>

### Rev Refresher

<<MUST item:7.3:rev_refresher>>
_Why: Currency_

> _Standard text:_ Refresher cadence check — annual refreshers actually delivered

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:7.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
