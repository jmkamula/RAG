---
leaf_id: req:A.5.25:triage_program_review
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Event Triage Program Review

> The triage program drifts when detection sources change, attack patterns evolve, or false-positive volume creeps. The review captures who reviewed the program, when, and the resulting calibration of detection sources, assessment criteria and classification scale

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.25:rev_date>>
_Why: 27002:5.25 — periodic_

<<TEXT>>

## 2. Reviewer identity (SecOps lead + InfoSec lead jointly)

<<MUST item:A.5.25:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. False-positive rate analysed across the period

<<MUST item:A.5.25:rev_fp_rate>>
_Why: Calibration_

<<TEXT>>

## 4. Missed-event analysis (events surfaced via lessons-learned that triage didn't catch)

<<MUST item:A.5.25:rev_missed>>
_Why: Closing the loop with A.5.27_

<<TEXT>>

## 5. Calibration outcome (detection sources / criteria / scale adjusted with rationale)

<<MUST item:A.5.25:rev_calibration>>
_Why: 27002:5.25 — keep current_

<<TEXT>>

## 6. Action items captured (e.g. add monitoring source, adjust severity threshold)

<<MUST item:A.5.25:rev_actions>>
_Why: 27002:5.25_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External threat intelligence input considered (link to A.5.7)

<<SHOULD item:A.5.25:rev_threat_intel>>
_Why: Detection landscape volatility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.25:rev_next_date>>
_Why: Planning_

<<TEXT>>
