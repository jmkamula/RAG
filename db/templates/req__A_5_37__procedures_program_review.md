---
leaf_id: req:A.5.37:procedures_program_review
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Operating Procedures Program Review

> Periodic verification that the register reflects the facility scope, procedures are still accurate (not just 'documented' but matching reality), availability mechanisms still work (operators can actually find them), and the maintenance procedure is being followed. Annual cadence (freshness=365) matches the records-family default — operational procedure methodology is stable, individual procedures get updated continuously via maintenance

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:A.5.37:rev_date>>
_Why: 27002:5.37 — documented + current_

<<TEXT>>

## 2. Reviewer identity and role recorded (operations lead + InfoSec lead jointly)

<<MUST item:A.5.37:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-procedure outcome (verified / amended / retired / new added) with availability-mechanism-still-works confirmation

<<MUST item:A.5.37:rev_register_check>>
_Why: 27002:5.37 — documented + available_

<<TEXT>>

## 4. Cross-check against the applicable-facilities scope — any new system / SaaS environment / facility class that should add procedures

<<MUST item:A.5.37:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Accuracy sampling — operator walked through a sample procedure end-to-end? procedure matches current system reality (UI screenshots current, commands work, dependencies still valid)

<<MUST item:A.5.37:rev_accuracy_sample>>
_Why: 27002:5.37 — operations_

<<TEXT>>

## 6. Emergency-use procedure review — confirmed available and accurate for DR/incident scenarios (these are the procedures where stale = catastrophic)

<<MUST item:A.5.37:rev_emergency_review>>
_Why: Operational realism_

<<TEXT>>

## 7. Changes propagated back to the live register with reference to this review

<<MUST item:A.5.37:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (major incident exposing procedure gap, M&A, major system migration)

<<SHOULD item:A.5.37:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.37:rev_next_date>>
_Why: Planning_

<<TEXT>>
