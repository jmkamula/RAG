---
leaf_id: req:A.7.1:perimeter_program_review
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Perimeter Program Review

> Periodic verification that perimeters still match the classification needs, the register reflects reality, and any site changes have been incorporated. Annual cadence (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.1:rev_date>>
_Why: 27002:7.1 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities lead + InfoSec lead jointly)

<<MUST item:A.7.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Physical walkthrough conducted per site (sample-based for multi-site orgs) — barriers verified present and functional

<<MUST item:A.7.1:rev_walkthrough>>
_Why: 27002:7.1 — verified_

<<TEXT>>

## 4. Cross-check against the applicable-sites scope — any new site or sub-let that should add a register entry

<<MUST item:A.7.1:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Changes propagated to the live register

<<MUST item:A.7.1:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
