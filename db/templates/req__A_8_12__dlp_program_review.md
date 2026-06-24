---
leaf_id: req:A.8.12:dlp_program_review
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Periodic DLP Program Review

> Periodic verification — ruleset currency, channel coverage gaps, true/false-positive trending, exception inventory (freshness=180; data-loss attack patterns evolve fast)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.12:rev_date>>
_Why: 27002:8.12 — periodic_

<<TEXT>>

## 2. Reviewer identity (DLP lead + Data Protection + InfoSec)

<<MUST item:A.8.12:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Channel-coverage gap check (new channel / new platform missing)

<<MUST item:A.8.12:rev_coverage_gaps>>
_Why: 27002:8.12 — measures_

<<TEXT>>

## 4. True-positive rate trending (detection effectiveness)

<<MUST item:A.8.12:rev_tp_rate>>
_Why: Detection effectiveness_

<<TEXT>>

## 5. Exception inventory re-confirmed / retired

<<MUST item:A.8.12:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 6. Baseline / ruleset / procedure updates published from findings

<<MUST item:A.8.12:rev_baseline_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.12:rev_next_date>>
_Why: Planning_

<<TEXT>>
