---
leaf_id: req:A.8.32:change_program_review
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Change Management Program Review

> Annual verification — register completeness, emergency-change ratio, rollback-attainment, change-induced-incident trending (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.32:rev_date>>
_Why: 27002:8.32 — periodic_

<<TEXT>>

## 2. Reviewer identity (Change Management lead + Engineering + InfoSec)

<<MUST item:A.8.32:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register-completeness sample (sample of production changes traced to register)

<<MUST item:A.8.32:rev_register_completeness>>
_Why: Drift prevention_

<<TEXT>>

## 4. Emergency-change ratio (high ratio signals process bypass)

<<MUST item:A.8.32:rev_emergency_ratio>>
_Why: Operational signal_

<<TEXT>>

## 5. Change-induced incident trending (cross-link to A.5.26 register — change as incident root cause)

<<MUST item:A.8.32:rev_change_incidents>>
_Why: Continuous improvement_

<<TEXT>>

## 6. Findings propagated to procedure / scope

<<MUST item:A.8.32:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.32:rev_next_date>>
_Why: Planning_

<<TEXT>>
