---
leaf_id: req:A.5.10:periodic_review
control_ref: A.5.10
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Periodic Acceptable Use Policy Review

<<DOC_CONTROL>>

> AUPs decay fast — new technologies (AI tools, new collaboration platforms), new regulations (data residency), and new threat patterns (social engineering vectors) all require policy updates. Review captures who reviewed, when, and whether the rules still cover the actual use patterns

<!-- TABLE-COLUMNS leaf:req:A.5.10:periodic_review -->
<!-- column: item:A.5.10:review_date -->
<!-- column: item:A.5.10:review_reviewer -->
<!-- column: item:A.5.10:review_outcome -->
<!-- column: item:A.5.10:review_use_patterns -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your Acceptable Use Policy up to date by tracking regular reviews, who performed them, and whether your rules still fit how your team actually works.

## When to use it

Use this template whenever you need to review your Acceptable Use Policy, which should happen about once a year or whenever your environment changes significantly.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 45 to 60 minutes completing this from scratch, depending on how many reviewers and usage patterns you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.10:periodic_review -->
| Review Date | Review Reviewer | Review Outcome | Review Use Patterns |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.10:periodic_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.10:review_date>>
_Why: Periodic review_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Review Reviewer

<<MUST item:A.5.10:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically CISO with HR and legal input)

<<GUIDANCE>>

### Review Outcome

<<MUST item:A.5.10:review_outcome>>
_Why: Periodic review_

> _Standard text:_ Outcome captured (no change / amended / re-issued) with rationale per amendment

<<GUIDANCE>>

### Review Use Patterns

<<MUST item:A.5.10:review_use_patterns>>
_Why: Drift catch_

> _Standard text:_ Use-pattern check — new technologies or behaviours that need explicit rules added

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.10:review_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers listed (new technology rollout, incident lessons-learned, regulatory change)

<<GUIDANCE>>

### Review Next Date

<<SHOULD item:A.5.10:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
