---
leaf_id: req:6.1.3:risk_treatment_program_review
control_ref: 6.1.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Risk Treatment Program Review

> Annual verification that the plan is being executed, the SoA is current, residual risks remain accepted (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:6.1.3:rev_date>>
_Why: Clause 6.1.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (Risk Manager + ISMS Manager + risk owners as needed)

<<MUST item:6.1.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Plan progress check — every treatment item status updated

<<MUST item:6.1.3:rev_plan_progress>>
_Why: 8.3 link_

<<TEXT>>

## 4. SoA currency check — still matches treatment plan + Annex A version

<<MUST item:6.1.3:rev_soa_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Residual risks re-affirmed by owners (or re-treatment triggered)

<<MUST item:6.1.3:rev_residual_reaffirm>>
_Why: Clause 6.1.3f_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:6.1.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
