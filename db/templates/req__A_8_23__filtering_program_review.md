---
leaf_id: req:A.8.23:filtering_program_review
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Web Filtering Program Review

<<DOC_CONTROL>>

> Annual verification — category-list currency, override-volume trending, malware-hit follow-through, coverage gaps (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.23:filtering_program_review -->
<!-- column: item:A.8.23:rev_date -->
<!-- column: item:A.8.23:rev_reviewer -->
<!-- column: item:A.8.23:rev_category_currency -->
<!-- column: item:A.8.23:rev_override_trending -->
<!-- column: item:A.8.23:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your web filtering program by recording annual checks on category lists, override trends, malware incidents, and coverage gaps. It ensures your controls stay up to date and effective.

## When to use it

Use this template once a year to review your web filtering program, making sure it always aligns with your environment and meets ISO 27001 requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as you'll need to fill in several key details for a thorough annual review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.23:filtering_program_review -->
| Rev Date | Rev Reviewer | Rev Category Currency | Rev Override Trending | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.23:filtering_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.23:rev_date>>
_Why: 27002:8.23 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.23:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Security Operations + Legal/HR for category boundaries)

<<GUIDANCE>>

### Rev Category Currency

<<MUST item:A.8.23:rev_category_currency>>
_Why: 27002:8.23 — managed_

> _Standard text:_ Category-list currency check (new malicious-content categories added; obsolete categories retired)

<<GUIDANCE>>

### Rev Override Trending

<<MUST item:A.8.23:rev_override_trending>>
_Why: Operational signal_

> _Standard text:_ Override-volume trending (spikes may indicate category over-blocking or coverage gap)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.23:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.23:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
