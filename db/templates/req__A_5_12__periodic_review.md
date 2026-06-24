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
---

# Periodic Classification Scheme Review

> Classification schemes are the foundation of handling controls — a stale scheme produces stale handling. Review checks whether the levels still match the actual sensitivity gradient, whether new categories have emerged (e.g. AI training corpora), and whether downstream controls (A.5.13, A.5.10, A.5.14) still align

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.12:review_date>>
_Why: Periodic review_

<<TEXT>>

## 2. Reviewer identity and role (typically CISO with data-protection and business-line input)

<<MUST item:A.5.12:review_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome captured (no change / amended / re-issued) with rationale per amendment

<<MUST item:A.5.12:review_outcome>>
_Why: Periodic review_

<<TEXT>>

## 4. Downstream-control alignment checked (A.5.13 labelling rules, A.5.10 handling rules, A.5.14 transfer still consistent)

<<MUST item:A.5.12:review_downstream>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers listed (M&A, new regulator-imposed classes, new business line with novel sensitivities)

<<SHOULD item:A.5.12:review_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.12:review_next_date>>
_Why: Planning_

<<TEXT>>
