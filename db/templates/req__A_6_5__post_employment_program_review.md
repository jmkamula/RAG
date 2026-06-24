---
leaf_id: req:A.6.5:post_employment_program_review
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Post-Employment Program Review

> Periodic verification that every leaver in the period was briefed, that the obligation scope still matches current law, and that any breach incidents have been handled per the enforcement approach. Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.5:rev_date>>
_Why: 27002:6.5 — periodic_

<<TEXT>>

## 2. Reviewer identity (HR lead + InfoSec lead + Legal counsel)

<<MUST item:A.6.5:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Briefing coverage check — every leaver in the period received and acknowledged a briefing (the register's completeness gate)

<<MUST item:A.6.5:rev_briefing_coverage>>
_Why: 27002:6.5 — completeness_

<<TEXT>>

## 4. Employment-law drift check per jurisdiction (legal counsel input on enforceability changes)

<<MUST item:A.6.5:rev_legal_drift>>
_Why: 27002:6.5 — applicable laws_

<<TEXT>>

## 5. Breach history review — any post-employment breaches occurred? handled per enforcement approach? lessons captured?

<<MUST item:A.6.5:rev_breach_history>>
_Why: 27002:6.5 — enforced_

<<TEXT>>

## 6. Changes propagated to the procedure / scope with reference to this review

<<MUST item:A.6.5:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (high-profile leaver, regulator action affecting post-employment terms, employment-tribunal ruling)

<<SHOULD item:A.6.5:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.5:rev_next_date>>
_Why: Planning_

<<TEXT>>
