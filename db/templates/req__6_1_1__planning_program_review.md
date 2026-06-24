---
leaf_id: req:6.1.1:planning_program_review
control_ref: 6.1.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Planning Program Review

> Annual verification that planning inputs are being consumed, the action register is current, effectiveness is being evaluated (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:6.1.1:rev_date>>
_Why: Clause 6.1.1 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + executive sponsor)

<<MUST item:6.1.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Inputs currency check — 4.1 + 4.2 reviewed before this planning cycle

<<MUST item:6.1.1:rev_inputs_currency>>
_Why: Cross-clause coherence_

<<TEXT>>

## 4. Action register currency check — every row reviewed for status + relevance

<<MUST item:6.1.1:rev_register_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Effectiveness summary across completed actions

<<MUST item:6.1.1:rev_effectiveness>>
_Why: Clause 6.1.1 — evaluate effectiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:6.1.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
