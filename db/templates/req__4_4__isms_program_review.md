---
leaf_id: req:4.4:isms_program_review
control_ref: 4.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# ISMS Manual Program Review

<<DOC_CONTROL>>

> Annual verification that the manual reflects current ISMS reality, the process map is current, and any changes were captured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:4.4:isms_program_review -->
<!-- column: item:4.4:rev_date -->
<!-- column: item:4.4:rev_reviewer -->
<!-- column: item:4.4:rev_currency -->
<!-- column: item:4.4:rev_map_currency -->
<!-- column: item:4.4:rev_change_log -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of the ISMS manual, ensuring it accurately reflects your current information security practices and any recent changes.

## When to use it

Use this template once a year to confirm your ISMS manual and process map are up to date, and to record any updates or changes made over the past 12 months.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this review from scratch, as each required section takes around 10–15 minutes to fill out.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.4:isms_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Map Currency | Rev Change Log |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.4:isms_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:4.4:rev_date>>
_Why: Clause 4.4 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:4.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + top management sponsor)

<<GUIDANCE>>

### Rev Currency

<<MUST item:4.4:rev_currency>>
_Why: Drift detection_

> _Standard text:_ Currency check — manual still matches how the ISMS actually runs

<<GUIDANCE>>

### Rev Map Currency

<<MUST item:4.4:rev_map_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Process map currency check (cross-leaf coherence)

<<GUIDANCE>>

### Rev Change Log

<<MUST item:4.4:rev_change_log>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against change records — every actual change in the year is logged

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:4.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
