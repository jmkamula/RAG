---
leaf_id: req:A.7.8:siting_program_review
control_ref: A.7.8
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Equipment Siting Program Review

> Annual verification that equipment is sited per its class requirements and the register is current. Freshness=365

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.8:rev_date>>
_Why: 27002:7.8 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec)

<<MUST item:A.7.8:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Physical walkthrough (sample-based) — siting verified, tamper-evidence intact

<<MUST item:A.7.8:rev_walkthrough>>
_Why: 27002:7.8 — implemented_

<<TEXT>>

## 4. Per-equipment outcome (verified / amended / remediated)

<<MUST item:A.7.8:rev_register_check>>
_Why: 27002:7.8 — current_

<<TEXT>>

## 5. Changes propagated to the live register

<<MUST item:A.7.8:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.8:rev_next_date>>
_Why: Planning_

<<TEXT>>
