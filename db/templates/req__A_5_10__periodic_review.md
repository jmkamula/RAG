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
---

# Periodic Acceptable Use Policy Review

> AUPs decay fast — new technologies (AI tools, new collaboration platforms), new regulations (data residency), and new threat patterns (social engineering vectors) all require policy updates. Review captures who reviewed, when, and whether the rules still cover the actual use patterns

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.10:review_date>>
_Why: Periodic review_

<<TEXT>>

## 2. Reviewer identity and role (typically CISO with HR and legal input)

<<MUST item:A.5.10:review_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome captured (no change / amended / re-issued) with rationale per amendment

<<MUST item:A.5.10:review_outcome>>
_Why: Periodic review_

<<TEXT>>

## 4. Use-pattern check — new technologies or behaviours that need explicit rules added

<<MUST item:A.5.10:review_use_patterns>>
_Why: Drift catch_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers listed (new technology rollout, incident lessons-learned, regulatory change)

<<SHOULD item:A.5.10:review_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.10:review_next_date>>
_Why: Planning_

<<TEXT>>
