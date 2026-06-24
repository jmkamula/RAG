---
leaf_id: req:A.5.1:annual_review
control_ref: A.5.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 3
should_count: 2
---

# Periodic Information Security Policy Review Record

> A.5.1 requires the policy to be reviewed at planned intervals (typically annually) and after significant changes. The review record captures who reviewed it, when, and the outcome (unchanged / amended / retired). Annual cadence (365d) — master InfoSec policy is stable; topic-specific policies they reference may move faster

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned review interval (typically within 12 months of last review)

<<MUST item:A.5.1:review_date>>
_Why: 27002:5.1 — reviewed at planned intervals_

<<TEXT>>

## 2. Outcome of the review (no change / amended to vN / retired)

<<MUST item:A.5.1:review_outcome>>
_Why: 27002:5.1 — reviewed_

<<TEXT>>

## 3. Reviewer identity and role

<<MUST item:A.5.1:review_reviewer>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. List of significant-change triggers that should prompt an ad-hoc review

<<SHOULD item:A.5.1:review_triggers>>
_Why: 27002:5.1 — review on significant change_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.1:review_next_date>>
_Why: Planning_

<<TEXT>>
