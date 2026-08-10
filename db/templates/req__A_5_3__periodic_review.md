---
leaf_id: req:A.5.3:periodic_review
control_ref: A.5.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Periodic Segregation of Duties Review

<<DOC_CONTROL>>

> Org structure shifts (new roles, reorganisations, M&A) create new conflict pairs and obsolete old ones. The review captures who reviewed the matrix, when, and the outcome — and propagates corrections back to the matrix and compensating controls

<!-- TABLE-COLUMNS leaf:req:A.5.3:periodic_review -->
<!-- column: item:A.5.3:review_date -->
<!-- column: item:A.5.3:review_reviewer -->
<!-- column: item:A.5.3:review_outcome -->
<!-- column: item:A.5.3:review_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you regularly check and document whether your team’s duties are properly separated, especially after changes in roles or company structure. It ensures any conflicts are identified and corrected, keeping your controls up to date.

## When to use it

Use this template whenever you need to review your segregation of duties, which should happen at least once a year or whenever there are changes in your organization’s structure or roles.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing the required sections for a typical review, plus additional time for each person or role you need to assess.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.3:periodic_review -->
| Review Date | Review Reviewer | Review Outcome | Review Actions |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.3:periodic_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.3:review_date>>
_Why: 27002:5.3 — periodic review_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Review Reviewer

<<MUST item:A.5.3:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically risk owner or compliance lead with input from function leads)

<<GUIDANCE>>

### Review Outcome

<<MUST item:A.5.3:review_outcome>>
_Why: 27002:5.3_

> _Standard text:_ Outcome per conflict pair (no change / amended / retired / new pair added)

<<GUIDANCE>>

### Review Actions

<<MUST item:A.5.3:review_actions>>
_Why: 27002:5.3c — risk-based_

> _Standard text:_ Actions captured where compensating controls failed in practice (operational incidents, audit findings)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.3:review_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers listed (reorg, M&A, new business line, key role departure) prompting unscheduled review

<<GUIDANCE>>

### Review Next Date

<<SHOULD item:A.5.3:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
