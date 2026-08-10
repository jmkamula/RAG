---
leaf_id: req:A.7.4.7:program_review
control_ref: A.7.4.7
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Retention Program Review

<<DOC_CONTROL>>

> Annual verification — retention schedules current, deletion triggers fire, no PII retained past schedule, conflicts documented (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.7:program_review -->
<!-- column: item:A.7.4.7:rev_date -->
<!-- column: item:A.7.4.7:rev_reviewer -->
<!-- column: item:A.7.4.7:rev_currency_check -->
<!-- column: item:A.7.4.7:rev_deletion_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your data retention program, making sure your schedules are up to date, deletion processes work, and no personal data is kept longer than allowed.

## When to use it

Use this review record if your organization needs to check its retention schedules and deletion processes, especially when your activities match certain privacy triggers. Plan to complete this about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 40 to 60 minutes filling this out from scratch, depending on how many records you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.7:program_review -->
| Rev Date | Rev Reviewer | Rev Currency Check | Rev Deletion Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.7:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.7:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal + Records Management)

<<GUIDANCE>>

### Rev Currency Check

<<MUST item:A.7.4.7:rev_currency_check>>
_Why: §7.4.7 — retention schedules_

> _Standard text:_ Schedule currency check — recent regulatory / business changes reflected

<<GUIDANCE>>

### Rev Deletion Audit

<<MUST item:A.7.4.7:rev_deletion_audit>>
_Why: Effectiveness_

> _Standard text:_ Deletion audit — sampled records past schedule verified deleted per A.7.4.5

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
