---
leaf_id: req:A.5.2:annual_review
control_ref: A.5.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 3
should_count: 2
---

# Periodic Roles and Responsibilities Review Record

> ISO 27002:2022 § 5.2 implementation guidance treats role allocation as needing periodic review to keep up with organizational change. The review record captures who reviewed the matrix, when, and the outcome (unchanged / re-allocated / new role introduced)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned review interval (typically within 12 months of last review)

<<MUST item:A.5.2:review_date>>
_Why: 27002:5.2 — periodic review_

<<TEXT>>

## 2. Outcome of the review (no change / amended to vN / role added or removed)

<<MUST item:A.5.2:review_outcome>>
_Why: 27002:5.2_

<<TEXT>>

## 3. Reviewer identity and role

<<MUST item:A.5.2:review_reviewer>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. List of significant-change triggers (reorg, new business line, key role departure) that should prompt an ad-hoc review

<<SHOULD item:A.5.2:review_triggers>>
_Why: 27002:5.2 — change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.2:review_next_date>>
_Why: Planning_

<<TEXT>>
