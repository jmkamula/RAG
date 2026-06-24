---
leaf_id: req:A.5.27:lessons_program_review
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Lessons-Learned Program Review

> The lessons program creates value only if it closes the loop — actions actually get done, lessons reduce repeat incidents, and the patterns drive systemic improvements. The review captures the planned-interval check: action-closure rate, repeat-incident detection, training-impact evidence, feedback-loop effectiveness and resulting program adjustments

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.27:rev_date>>
_Why: 27002:5.27 — periodic_

<<TEXT>>

## 2. Reviewer identity (program owner + InfoSec lead jointly)

<<MUST item:A.5.27:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Action-closure rate analysed (open / aged / closed) against targets

<<MUST item:A.5.27:rev_closure_rate>>
_Why: 27002:5.27a_

<<TEXT>>

## 4. Repeat-incident analysis (lessons that should have prevented later incidents — did they?)

<<MUST item:A.5.27:rev_repeat>>
_Why: 27002:5.27a,e_

<<TEXT>>

## 5. Training-impact evidence reviewed where lessons drove curriculum changes

<<MUST item:A.5.27:rev_training_impact>>
_Why: 27002:5.27d_

<<TEXT>>

## 6. Action items captured for the program (e.g. tighten root-cause typing, expand pattern scope)

<<MUST item:A.5.27:rev_actions>>
_Why: 27002:5.27_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External benchmark or industry-practice input considered

<<SHOULD item:A.5.27:rev_benchmark>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.27:rev_next_date>>
_Why: Planning_

<<TEXT>>
