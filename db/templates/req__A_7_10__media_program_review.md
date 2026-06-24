---
leaf_id: req:A.7.10:media_program_review
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Storage Media Program Review

> Annual verification of register currency, lifecycle compliance, lost-media incidents. Freshness=365

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.10:rev_date>>
_Why: 27002:7.10 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT + InfoSec)

<<MUST item:A.7.10:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Inventory audit — sample-based confirmation of media at stated location

<<MUST item:A.7.10:rev_inventory_audit>>
_Why: Loss detection_

<<TEXT>>

## 4. Lost-media count for period (every loss has an incident link)

<<MUST item:A.7.10:rev_lost_count>>
_Why: 27002:7.10 — protected_

<<TEXT>>

## 5. Changes propagated to the register / procedure

<<MUST item:A.7.10:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.10:rev_next_date>>
_Why: Planning_

<<TEXT>>
