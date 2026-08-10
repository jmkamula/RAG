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
table_shape: true
---

# Periodic Project-Security Program Review

<<DOC_CONTROL>>

> The gate process creates value only if it's catching things — projects with skipped gates, late-detected security issues, and tiering-misclassifications all signal the program is leaking. The review captures the planned-interval check: gate-skip rate, late-detection analysis, tier-mix shifts, InfoSec capacity vs project demand, and resulting program adjustments. Annual cadence — methodology stability outweighs short-cycle drift

<!-- TABLE-COLUMNS leaf:req:A.5.8:project_security_program_review -->
<!-- column: item:A.5.8:rev_date -->
<!-- column: item:A.5.8:rev_reviewer -->
<!-- column: item:A.5.8:rev_gate_skip -->
<!-- column: item:A.5.8:rev_late_detection -->
<!-- column: item:A.5.8:rev_tiering -->
<!-- column: item:A.5.8:rev_capacity -->
<!-- column: item:A.5.8:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track and review your security program’s effectiveness by recording skipped project gates, late security detections, tiering issues, and how well InfoSec resources are meeting project demands. It supports ongoing improvements and compliance with ISO 27001 requirements.

## When to use it

Use this template for a comprehensive review of your project security program every year, or whenever you need to check for gaps like missed gates or late security findings. It applies to all environments on a regular annual basis.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this review from scratch, depending on the number of projects and the detail required for each section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.8:project_security_program_review -->
| Rev Date | Rev Reviewer | Rev Gate Skip | Rev Late Detection | Rev Tiering | Rev Capacity | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.8:project_security_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.8:rev_date>>
_Why: 27002:5.8 — periodic_

> _Standard text:_ Review date within the planned annual interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec lead + PMO/project office head jointly)

<<GUIDANCE>>

### Rev Gate Skip

<<MUST item:A.5.8:rev_gate_skip>>
_Why: 27002:5.8 — assurance_

> _Standard text:_ Gate-skip rate analysed (projects that bypassed gates; root cause and remediation per skip)

<<GUIDANCE>>

### Rev Late Detection

<<MUST item:A.5.8:rev_late_detection>>
_Why: Program effectiveness_

> _Standard text:_ Late-detection analysis (security issues surfaced at or after go-live that should have been caught earlier)

<<GUIDANCE>>

### Rev Tiering

<<MUST item:A.5.8:rev_tiering>>
_Why: 27002:5.8 — proportionality calibration_

> _Standard text:_ Tiering audit (sample of projects re-tiered to validate the tier criteria are still calibrated to actual risk)

<<GUIDANCE>>

### Rev Capacity

<<MUST item:A.5.8:rev_capacity>>
_Why: 27002:5.8 — sustainable defined responsibilities_

> _Standard text:_ InfoSec capacity vs project pipeline reviewed (gates fail silently when reviewer capacity is exhausted)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.8:rev_actions>>
_Why: 27002:5.8 — program adjustments_

> _Standard text:_ Action items captured for the program (e.g. update templates, retrain PMs, tighten tiering criteria, add reviewer capacity)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Methodology

<<SHOULD item:A.5.8:rev_methodology>>
_Why: Audit defensibility_

> _Standard text:_ Methodology check (does the gate model still fit the org's delivery mix — waterfall vs agile vs hybrid)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
