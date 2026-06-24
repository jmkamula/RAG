---
leaf_id: req:Art.44:transfer_program_review
control_ref: Art.44
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Transfer Program Review

> Annual verification — every active transfer has a current Art.45/46/47/49 mechanism, register reflects current vendor landscape, Schrems II-style TIA considerations applied (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.44:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal counsel + procurement)

<<MUST item:Art.44:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register currency — every flagged transfer in last-assessment freshness window

<<MUST item:Art.44:rev_register_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Mechanism-validity sample — Art.45 adequacy decisions, Art.46 SCCs, Art.47 BCRs all current versions / approvals

<<MUST item:Art.44:rev_mechanism_validity>>
_Why: Art.44-49_

<<TEXT>>

## 5. Silent-transfer sweep — verify no new vendor or service-shape change created an unflagged transfer

<<MUST item:Art.44:rev_silent_transfer_sweep>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.44:rev_next_date>>
_Why: Planning_

<<TEXT>>
