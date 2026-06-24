---
leaf_id: req:A.6.1:screening_program_review
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Screening Program Review

> Periodic verification that screening is happening at the right depth for each role tier, that legal/sectoral driver shifts have been incorporated, that re-screening cadence is being met, and that the register has no gaps. Annual cadence (freshness=365) matches the HR-program-review doctrine

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.1:rev_date>>
_Why: 27002:6.1 — periodic_

<<TEXT>>

## 2. Reviewer identity and role recorded (HR lead + InfoSec lead jointly; legal-counsel sign-off where jurisdictional shifts material)

<<MUST item:A.6.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-tier outcome (did every new hire in this tier get the right checks? gaps flagged and remediated)

<<MUST item:A.6.1:rev_register_check>>
_Why: 27002:6.1 — completeness_

<<TEXT>>

## 4. Cross-check against the applicable-roles scope — any new role tier, new jurisdiction, new sectoral driver?

<<MUST item:A.6.1:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Rescreen status — for roles with ongoing-check obligations, what fraction completed on cadence vs aged-overdue

<<MUST item:A.6.1:rev_rescreen_status>>
_Why: Operational discipline_

<<TEXT>>

## 6. Changes propagated back to the procedure / scope with reference to this review

<<MUST item:A.6.1:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (regulator enforcement action in sector, security incident involving inadequately-screened personnel)

<<SHOULD item:A.6.1:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
