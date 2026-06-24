---
leaf_id: req:Art.45:adequacy_program_review
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Adequacy Program Review

> Annual verification — adequacy decisions still in force, recipient eligibility re-checked, invalidation watch maintained (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.45:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal counsel)

<<MUST item:Art.45:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Decision currency — every cited adequacy decision still in force (not repealed, suspended, or invalidated)

<<MUST item:Art.45:rev_decision_currency>>
_Why: Art.45.5_

<<TEXT>>

## 4. Recipient-eligibility recheck — certifications still active (US-DPF, etc.)

<<MUST item:Art.45:rev_recipient_recheck>>
_Why: Defensibility_

<<TEXT>>

## 5. Fallback readiness — if a decision were invalidated, Art.46 fallback (e.g. SCCs) pre-staged with affected vendors

<<MUST item:Art.45:rev_fallback_readiness>>
_Why: Operational resilience_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.45:rev_next_date>>
_Why: Planning_

<<TEXT>>
