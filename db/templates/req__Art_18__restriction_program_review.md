---
leaf_id: req:Art.18:restriction_program_review
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Restriction Program Review

> Annual verification — restrictions still active are valid, Art.18.2 exceptions enforced, Art.19 notifications fired (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.18:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + ops lead)

<<MUST item:Art.18:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Active-restrictions check — every active row still has a valid Art.18.1 ground

<<MUST item:Art.18:rev_active_restrictions>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Exception compliance — restricted records only used per Art.18.2 exceptions

<<MUST item:Art.18:rev_exception_compliance>>
_Why: Art.18.2_

<<TEXT>>

## 5. Art.19 notification compliance — recipient notifications fired for new/lifted restrictions

<<MUST item:Art.18:rev_art19_compliance>>
_Why: Art.19_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.18:rev_next_date>>
_Why: Planning_

<<TEXT>>
