---
leaf_id: req:Art.22:automated_decision_program_review
control_ref: Art.22
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Automated Decision-Making Program Review

> Annual verification — every in-scope system has a current Art.22.2 basis, safeguards functioning, DPIAs current, objections handled (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.22:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + ML/product lead)

<<MUST item:Art.22:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Basis currency check — every in-scope system still has valid Art.22.2 basis

<<MUST item:Art.22:rev_basis_currency>>
_Why: Art.22.2_

<<TEXT>>

## 4. Safeguards health — human intervention queue actually used, contest mechanism functioning

<<MUST item:Art.22:rev_safeguards_health>>
_Why: Art.22.3_

<<TEXT>>

## 5. Silent-promotion sweep — verify no flag-for-review system has been quietly promoted to solely-automated without procedure update

<<MUST item:Art.22:rev_silent_promotion>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.22:rev_next_date>>
_Why: Planning_

<<TEXT>>
