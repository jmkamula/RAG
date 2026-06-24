---
leaf_id: req:9.3:management_review_program_review
control_ref: 9.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Management Review Program Review

> Annual verification that reviews happened on cadence, all required inputs were considered, decisions are being tracked to closure (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:9.3:rev_date>>
_Why: Clause 9.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager)

<<MUST item:9.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Cadence check — every planned review happened (or was rescheduled with rationale)

<<MUST item:9.3:rev_cadence_met>>
_Why: Clause 9.3.1_

<<TEXT>>

## 4. Inputs-completeness check — every 9.3.2 a-g input was present in each review's minutes

<<MUST item:9.3:rev_inputs_completeness>>
_Why: Clause 9.3.2_

<<TEXT>>

## 5. Action-closure check — decisions from prior reviews tracked to 10.1/10.2 closure

<<MUST item:9.3:rev_action_closure>>
_Why: Clause 9.3.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:9.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
