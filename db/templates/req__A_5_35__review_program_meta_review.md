---
leaf_id: req:A.5.35:review_program_meta_review
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Independent Review Program Meta-Review

> The review program itself needs review — are we picking reviewers that stay genuinely independent, is the cadence right, are findings closing, do reviews surface real issues or have they become rubber-stamps? The meta-review evidences periodic self-assessment of the review program and resulting adjustments

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Meta-review date within the planned interval

<<MUST item:A.5.35:pgm_date>>
_Why: 27002:5.35 — periodic_

<<TEXT>>

## 2. Reviewer identity (program owner + InfoSec lead jointly + audit committee chair where applicable)

<<MUST item:A.5.35:pgm_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Independence-discipline check — did the actual reviewers meet the criteria? rotation worked? any reviewer reviewing their own area?

<<MUST item:A.5.35:pgm_independence_check>>
_Why: 27002:5.35 — reviewed independently_

<<TEXT>>

## 4. Coverage check — did the schedule actually run? all planned scope areas reviewed?

<<MUST item:A.5.35:pgm_coverage>>
_Why: 27002:5.35 — planned intervals_

<<TEXT>>

## 5. Findings-closure rate across the program (open / aged / closed)

<<MUST item:A.5.35:pgm_closure>>
_Why: Operational discipline_

<<TEXT>>

## 6. Cadence-adjustment or scope-adjustment decisions (tighten / loosen / re-tier / change reviewer pool)

<<MUST item:A.5.35:pgm_outcome>>
_Why: 27002:5.35 — adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External benchmarking or industry-practice input considered

<<SHOULD item:A.5.35:pgm_benchmark>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned meta-review date stated

<<SHOULD item:A.5.35:pgm_next_date>>
_Why: Planning_

<<TEXT>>
