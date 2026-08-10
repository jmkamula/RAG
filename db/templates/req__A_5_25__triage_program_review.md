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
table_shape: true
---

# Periodic Event Triage Program Review

<<DOC_CONTROL>>

> The triage program drifts when detection sources change, attack patterns evolve, or false-positive volume creeps. The review captures who reviewed the program, when, and the resulting calibration of detection sources, assessment criteria and classification scale

<!-- TABLE-COLUMNS leaf:req:A.5.25:triage_program_review -->
<!-- column: item:A.5.25:rev_date -->
<!-- column: item:A.5.25:rev_reviewer -->
<!-- column: item:A.5.25:rev_fp_rate -->
<!-- column: item:A.5.25:rev_missed -->
<!-- column: item:A.5.25:rev_calibration -->
<!-- column: item:A.5.25:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document regular reviews of your event triage program, capturing who performed the review, when it happened, and any updates made to detection sources or assessment criteria.

## When to use it

Use this template whenever you review your event triage program, which should happen about every six months or whenever your environment changes in ways that could affect detection or classification.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of required details and the complexity of your program updates.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.25:triage_program_review -->
| Rev Date | Rev Reviewer | Rev Fp Rate | Rev Missed | Rev Calibration | Rev Actions |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.25:triage_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.25:rev_date>>
_Why: 27002:5.25 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.25:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (SecOps lead + InfoSec lead jointly)

<<GUIDANCE>>

### Rev Fp Rate

<<MUST item:A.5.25:rev_fp_rate>>
_Why: Calibration_

> _Standard text:_ False-positive rate analysed across the period

<<GUIDANCE>>

### Rev Missed

<<MUST item:A.5.25:rev_missed>>
_Why: Closing the loop with A.5.27_

> _Standard text:_ Missed-event analysis (events surfaced via lessons-learned that triage didn't catch)

<<GUIDANCE>>

### Rev Calibration

<<MUST item:A.5.25:rev_calibration>>
_Why: 27002:5.25 — keep current_

> _Standard text:_ Calibration outcome (detection sources / criteria / scale adjusted with rationale)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.25:rev_actions>>
_Why: 27002:5.25_

> _Standard text:_ Action items captured (e.g. add monitoring source, adjust severity threshold)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Threat Intel

<<SHOULD item:A.5.25:rev_threat_intel>>
_Why: Detection landscape volatility_

> _Standard text:_ External threat intelligence input considered (link to A.5.7)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.25:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
