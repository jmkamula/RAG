---
leaf_id: req:A.5.4:periodic_review
control_ref: A.5.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
---

# Periodic Review of the Management Directive

> The directive must stay aligned with the policy framework it references — when policies are renamed, retired, or added the directive becomes stale. Review captures who reviewed, when, and whether the policy references and enforcement linkages still hold

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.4:review_date>>
_Why: Periodic review_

<<TEXT>>

## 2. Reviewer identity and role (typically CISO or compliance lead, validated by top management)

<<MUST item:A.5.4:review_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome captured (no change / amended / re-issued) and policy-reference drift checked

<<MUST item:A.5.4:review_outcome>>
_Why: Periodic review_

<<TEXT>>

## 4. Actions captured where the directive needed amendment (policy reorg, scope change, new personnel categories)

<<MUST item:A.5.4:review_actions>>
_Why: Continual improvement_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers listed (major policy reorg, M&A, regulatory change) prompting unscheduled review

<<SHOULD item:A.5.4:review_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.4:review_next_date>>
_Why: Planning_

<<TEXT>>
