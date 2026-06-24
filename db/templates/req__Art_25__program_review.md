---
leaf_id: req:Art.25:program_review
control_ref: Art.25
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# DPbD Program Review

> Annual verification — DPbD reviews happened for every in-scope design, defaults register is current, certification reliance still valid (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.25:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + product + engineering)

<<MUST item:Art.25:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Design-coverage check — every in-scope design activity had a DPbD review

<<MUST item:Art.25:rev_coverage>>
_Why: Art.25.1_

<<TEXT>>

## 4. Defaults register currency check (cross-leaf — defaults still match deployed system state)

<<MUST item:Art.25:rev_defaults_currency>>
_Why: Art.25.2_

<<TEXT>>

## 5. If Art.25.3 certification used — certification still in validity period

<<MUST item:Art.25:rev_certification_validity>>
_Why: Art.25.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.25:rev_next_date>>
_Why: Planning_

<<TEXT>>
