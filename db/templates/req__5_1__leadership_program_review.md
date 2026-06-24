---
leaf_id: req:5.1:leadership_program_review
control_ref: 5.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Leadership Program Review

> Annual verification that leadership commitment is being visibly demonstrated — directive signed and current, framework being followed, reaffirmations on cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:5.1:rev_date>>
_Why: Clause 5.1 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + non-executive director if available)

<<MUST item:5.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Directive currency check — signed by current top management

<<MUST item:5.1:rev_directive_currency>>
_Why: Drift detection_

<<TEXT>>

## 4. Framework adherence check — board cadence happened, sponsor activities completed

<<MUST item:5.1:rev_framework_adherence>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Reaffirmation record completeness — required reaffirmations all present

<<MUST item:5.1:rev_reaffirmation_completeness>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:5.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
