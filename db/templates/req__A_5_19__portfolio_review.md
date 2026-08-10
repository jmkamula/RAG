---
leaf_id: req:A.5.19:portfolio_review
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Periodic Supplier Portfolio Review

<<DOC_CONTROL>>

> A.5.19 expects periodic review of the supplier portfolio — to refresh risk classifications, re-test selection criteria, and confirm that monitoring and training arrangements still fit the supplier mix

<!-- TABLE-COLUMNS leaf:req:A.5.19:portfolio_review -->
<!-- column: item:A.5.19:rev_date -->
<!-- column: item:A.5.19:rev_reviewer -->
<!-- column: item:A.5.19:rev_outcome -->
<!-- column: item:A.5.19:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your suppliers by reviewing their risk levels, selection criteria, and ongoing monitoring or training needs. It's designed to make sure your supplier management stays up to date and compliant.

## When to use it

Use this template whenever you need to review your supplier portfolio, which should happen at least once a year to stay aligned with ISO 27001 requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of suppliers you have and the detail required for each entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.19:portfolio_review -->
| Rev Date | Rev Reviewer | Rev Outcome | Rev Actions |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.19:portfolio_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.19:rev_date>>
_Why: 27002:5.19e — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.19:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically procurement + InfoSec lead)

<<GUIDANCE>>

### Rev Outcome

<<MUST item:A.5.19:rev_outcome>>
_Why: 27002:5.19e_

> _Standard text:_ Outcome per supplier or per tier (no change / re-tiered / added / removed)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.19:rev_actions>>
_Why: 27002:5.19i,k_

> _Standard text:_ Action items captured where monitoring or training arrangements need adjustment

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Triggers

<<SHOULD item:A.5.19:rev_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers (M&A, market events, new business line, supplier incident) prompting unscheduled review

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.19:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
