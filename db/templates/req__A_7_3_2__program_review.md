---
leaf_id: req:A.7.3.2:program_review
control_ref: A.7.3.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Notice Content Program Review

<<DOC_CONTROL>>

> Annual verification — notices reflect current processing state, field coverage complete per context, updates issued on time (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.2:program_review -->
<!-- column: item:A.7.3.2:rev_date -->
<!-- column: item:A.7.3.2:rev_reviewer -->
<!-- column: item:A.7.3.2:rev_currency_audit -->
<!-- column: item:A.7.3.2:rev_field_completeness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and document that your notices are up-to-date, accurate, and cover all necessary fields for privacy compliance. It's designed to support annual checks and ensure your notices meet ISO 27701 requirements.

## When to use it

Use this template when your organization’s profile matches specific privacy triggers and you need to verify your notice content each year. It’s ideal for annual reviews to confirm your notices reflect current processing practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40–60 minutes completing this from scratch, as each required element takes 10–15 minutes to fill out. The total time may vary if you have multiple notices to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.2:program_review -->
| Rev Date | Rev Reviewer | Rev Currency Audit | Rev Field Completeness |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal + UX)

<<GUIDANCE>>

### Rev Currency Audit

<<MUST item:A.7.3.2:rev_currency_audit>>
_Why: §7.3.2 — updated information_

> _Standard text:_ Currency audit — sampled notices verified against A.7.2.1 purpose register + A.7.2.8 RoPA

<<GUIDANCE>>

### Rev Field Completeness

<<MUST item:A.7.3.2:rev_field_completeness>>
_Why: §7.3.2 — type of information_

> _Standard text:_ Field completeness — sampled notices verified against catalog

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
