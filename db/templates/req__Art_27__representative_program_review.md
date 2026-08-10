---
leaf_id: req:Art.27:representative_program_review
control_ref: Art.27
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Representative Program Review

<<DOC_CONTROL>>

> Annual verification — designation current, representative responsive, Art.27.2 exception assessment still valid (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.27:representative_program_review -->
<!-- column: item:Art.27:rev_date -->
<!-- column: item:Art.27:rev_reviewer -->
<!-- column: item:Art.27:rev_designation_currency -->
<!-- column: item:Art.27:rev_operations_sample -->
<!-- column: item:Art.27:rev_exception_recheck -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your GDPR representative arrangements, ensuring your designation is up to date and your exception assessment remains valid. It's designed for easy annual reviews and clear record-keeping.

## When to use it

Use this template if your organization is required to appoint a GDPR representative and needs to confirm compliance each year. Complete it whenever your business profile matches the relevant criteria, typically once every 12 months.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.27:representative_program_review -->
| Rev Date | Rev Reviewer | Rev Designation Currency | Rev Operations Sample | Rev Exception Recheck |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.27:representative_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.27:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.27:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

<<GUIDANCE>>

### Rev Designation Currency

<<MUST item:Art.27:rev_designation_currency>>
_Why: Art.27.1_

> _Standard text:_ Designation currency — representative still operating, mandate still valid

<<GUIDANCE>>

### Rev Operations Sample

<<MUST item:Art.27:rev_operations_sample>>
_Why: Effectiveness_

> _Standard text:_ Operations sample — interactions handled within SLAs, no failed escalations

<<GUIDANCE>>

### Rev Exception Recheck

<<MUST item:Art.27:rev_exception_recheck>>
_Why: Currency_

> _Standard text:_ Art.27.2 exception re-check where claimed — processing-pattern shift may invalidate the exception

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.27:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
