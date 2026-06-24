---
leaf_id: req:Art.29:processing_under_authority_program_review
control_ref: Art.29
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Processing Under Authority Program Review

> Annual verification — every person touching personal data has a current authorisation row, training is current, processing stays within documented instructions (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.29:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + HR + ops lead)

<<MUST item:Art.29:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Authorisation completeness — every person with access has a register row

<<MUST item:Art.29:rev_authorisation_completeness>>
_Why: Art.29 — under authority_

<<TEXT>>

## 4. Training currency — A.6.3 / 7.3 training current for every authorised person

<<MUST item:Art.29:rev_training_currency>>
_Why: Cross-control_

<<TEXT>>

## 5. Instruction-drift sweep — sample processing activities to verify they stay within documented controller instructions

<<MUST item:Art.29:rev_instruction_drift>>
_Why: Art.29 — only on documented instructions_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.29:rev_next_date>>
_Why: Planning_

<<TEXT>>
