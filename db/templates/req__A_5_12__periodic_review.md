---
leaf_id: req:A.5.12:periodic_review
control_ref: A.5.12
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Periodic Classification Scheme Review

> Classification schemes are the foundation of handling controls — a stale scheme produces stale handling. Review checks whether the levels still match the actual sensitivity gradient, whether new categories have emerged (e.g. AI training corpora), and whether downstream controls (A.5.13, A.5.10, A.5.14) still align

<!-- TABLE-COLUMNS leaf:req:A.5.12:periodic_review -->
<!-- column: item:A.5.12:review_date -->
<!-- column: item:A.5.12:review_reviewer -->
<!-- column: item:A.5.12:review_outcome -->
<!-- column: item:A.5.12:review_downstream -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.12:periodic_review -->
| Review Date | Review Reviewer | Review Outcome | Review Downstream |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.12:periodic_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.12:review_date>>
_Why: Periodic review_

> _Standard text:_ Review date within the planned interval

### Review Reviewer

<<MUST item:A.5.12:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically CISO with data-protection and business-line input)

### Review Outcome

<<MUST item:A.5.12:review_outcome>>
_Why: Periodic review_

> _Standard text:_ Outcome captured (no change / amended / re-issued) with rationale per amendment

### Review Downstream

<<MUST item:A.5.12:review_downstream>>
_Why: Cross-control coherence_

> _Standard text:_ Downstream-control alignment checked (A.5.13 labelling rules, A.5.10 handling rules, A.5.14 transfer still consistent)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.12:review_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers listed (M&A, new regulator-imposed classes, new business line with novel sensitivities)

### Review Next Date

<<SHOULD item:A.5.12:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
