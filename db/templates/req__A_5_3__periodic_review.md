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
---

# Periodic Segregation of Duties Review

> Org structure shifts (new roles, reorganisations, M&A) create new conflict pairs and obsolete old ones. The review captures who reviewed the matrix, when, and the outcome — and propagates corrections back to the matrix and compensating controls

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.3:review_date>>
_Why: 27002:5.3 — periodic review_

<<TEXT>>

## 2. Reviewer identity and role (typically risk owner or compliance lead with input from function leads)

<<MUST item:A.5.3:review_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome per conflict pair (no change / amended / retired / new pair added)

<<MUST item:A.5.3:review_outcome>>
_Why: 27002:5.3_

<<TEXT>>

## 4. Actions captured where compensating controls failed in practice (operational incidents, audit findings)

<<MUST item:A.5.3:review_actions>>
_Why: 27002:5.3c — risk-based_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers listed (reorg, M&A, new business line, key role departure) prompting unscheduled review

<<SHOULD item:A.5.3:review_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.3:review_next_date>>
_Why: Planning_

<<TEXT>>
