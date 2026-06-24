---
leaf_id: req:A.7.3:rooms_program_review
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Rooms Program Review

> Annual verification of room classifications, locking standards in place, and currency of the register (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.3:rev_date>>
_Why: 27002:7.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec)

<<MUST item:A.7.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Physical walkthrough conducted (sample-based) — locking standards verified, signage compliant

<<MUST item:A.7.3:rev_walkthrough>>
_Why: 27002:7.3 — verified_

<<TEXT>>

## 4. Per-room outcome (verified / amended / retired / new added)

<<MUST item:A.7.3:rev_register_check>>
_Why: 27002:7.3 — current_

<<TEXT>>

## 5. Changes propagated to the live register

<<MUST item:A.7.3:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
