---
leaf_id: req:A.6.3:awareness_programme_review
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Awareness Programme Review

> Periodic verification that the curriculum still matches current policies, the completion register has no gaps, effectiveness metrics are trending right, and awareness mechanisms are being executed. Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.3:rev_date>>
_Why: 27002:6.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (Security Awareness Lead + InfoSec lead jointly)

<<MUST item:A.6.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Completion rate analysis (overall % current; per-audience-segment % current; aged-overdue list)

<<MUST item:A.6.3:rev_completion_rate>>
_Why: 27002:6.3 — completeness_

<<TEXT>>

## 4. Effectiveness analysis (quiz pass-rate trend, phishing-simulation click-rate trend, reporting-rate trend per A.6.8)

<<MUST item:A.6.3:rev_effectiveness>>
_Why: 27002:6.3 — effectiveness_

<<TEXT>>

## 5. Curriculum currency check (referenced policies still align with the training content; new topics added per scope changes)

<<MUST item:A.6.3:rev_curriculum_check>>
_Why: 27002:6.3 — current_

<<TEXT>>

## 6. Changes propagated to the curriculum / register / scope with reference to this review

<<MUST item:A.6.3:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (major incident exposing awareness gap, new compliance regime, major tech adoption)

<<SHOULD item:A.6.3:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
