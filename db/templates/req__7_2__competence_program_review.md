---
leaf_id: req:7.2:competence_program_review
control_ref: 7.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Competence Program Review

> Annual verification that the record is current per role, every gap has a closure path, effectiveness is being evaluated for completed actions (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:7.2:rev_date>>
_Why: Clause 7.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (HR partner + ISMS Manager + relevant function heads)

<<MUST item:7.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Record currency check — turnover, role changes, new hires reflected

<<MUST item:7.2:rev_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Gap-closure progress check — open gaps either closed or on a remediation plan

<<MUST item:7.2:rev_gap_closure>>
_Why: Effectiveness_

<<TEXT>>

## 5. Effectiveness sample — completed actions actually changed observed competence

<<MUST item:7.2:rev_effectiveness>>
_Why: Clause 7.2 c)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:7.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
