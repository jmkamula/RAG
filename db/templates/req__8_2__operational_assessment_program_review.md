---
leaf_id: req:8.2:operational_assessment_program_review
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Operational Assessment Program Review

> Annual verification that planned assessments happened, significant-change triggers fired when they should have, results inform the treatment plan (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:8.2:rev_date>>
_Why: Clause 8.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (Risk Manager + ISMS Manager)

<<MUST item:8.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Cadence-met check — every scheduled assessment for each tier happened

<<MUST item:8.2:rev_cadence_met>>
_Why: Clause 8.2 — planned intervals_

<<TEXT>>

## 4. Trigger-firing sweep — significant changes during the year that should have triggered ad-hoc assessment all did

<<MUST item:8.2:rev_triggers_fired>>
_Why: Clause 8.2 — significant changes_

<<TEXT>>

## 5. Treatment handoff — every new risk found flows to 6.1.3 / 8.3 treatment

<<MUST item:8.2:rev_treatment_handoff>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:8.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
