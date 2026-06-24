---
leaf_id: req:A.5.8:project_security_program_review
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Project-Security Program Review

> The gate process creates value only if it's catching things — projects with skipped gates, late-detected security issues, and tiering-misclassifications all signal the program is leaking. The review captures the planned-interval check: gate-skip rate, late-detection analysis, tier-mix shifts, InfoSec capacity vs project demand, and resulting program adjustments. Annual cadence — methodology stability outweighs short-cycle drift

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned annual interval

<<MUST item:A.5.8:rev_date>>
_Why: 27002:5.8 — periodic_

<<TEXT>>

## 2. Reviewer identity (InfoSec lead + PMO/project office head jointly)

<<MUST item:A.5.8:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Gate-skip rate analysed (projects that bypassed gates; root cause and remediation per skip)

<<MUST item:A.5.8:rev_gate_skip>>
_Why: 27002:5.8 — assurance_

<<TEXT>>

## 4. Late-detection analysis (security issues surfaced at or after go-live that should have been caught earlier)

<<MUST item:A.5.8:rev_late_detection>>
_Why: Program effectiveness_

<<TEXT>>

## 5. Tiering audit (sample of projects re-tiered to validate the tier criteria are still calibrated to actual risk)

<<MUST item:A.5.8:rev_tiering>>
_Why: 27002:5.8 — proportionality calibration_

<<TEXT>>

## 6. InfoSec capacity vs project pipeline reviewed (gates fail silently when reviewer capacity is exhausted)

<<MUST item:A.5.8:rev_capacity>>
_Why: 27002:5.8 — sustainable defined responsibilities_

<<TEXT>>

## 7. Action items captured for the program (e.g. update templates, retrain PMs, tighten tiering criteria, add reviewer capacity)

<<MUST item:A.5.8:rev_actions>>
_Why: 27002:5.8 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Methodology check (does the gate model still fit the org's delivery mix — waterfall vs agile vs hybrid)

<<SHOULD item:A.5.8:rev_methodology>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.8:rev_next_date>>
_Why: Planning_

<<TEXT>>
