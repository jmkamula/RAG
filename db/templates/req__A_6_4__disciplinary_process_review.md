---
leaf_id: req:A.6.4:disciplinary_process_review
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Disciplinary Process Review

> Periodic verification that the process still aligns with current employment law per jurisdiction, that case outcomes show consistent application (not discriminatory), and that lessons from cases feed back to relevant controls. Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.4:rev_date>>
_Why: 27002:6.4 — periodic_

<<TEXT>>

## 2. Reviewer identity (HR lead + InfoSec lead + Legal counsel)

<<MUST item:A.6.4:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Consistency analysis — case outcomes reviewed for consistent application across cases / demographics (avoids discriminatory enforcement patterns)

<<MUST item:A.6.4:rev_consistency>>
_Why: Procedural fairness_

<<TEXT>>

## 4. Employment-law drift check per jurisdiction (legal counsel input)

<<MUST item:A.6.4:rev_legal_drift>>
_Why: 27002:6.4 — applicable laws_

<<TEXT>>

## 5. Lessons-propagation check — did case-driven lessons feed back to awareness curriculum (A.6.3), control updates, or policy amendments?

<<MUST item:A.6.4:rev_lessons_propagated>>
_Why: Continual improvement_

<<TEXT>>

## 6. Changes propagated to the procedure with reference to this review

<<MUST item:A.6.4:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (employment tribunal ruling affecting the process, regulator enforcement action, major incident with personnel involvement)

<<SHOULD item:A.6.4:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.4:rev_next_date>>
_Why: Planning_

<<TEXT>>
