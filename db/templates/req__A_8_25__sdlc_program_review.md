---
leaf_id: req:A.8.25:sdlc_program_review
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Periodic SDLC Program Review

> Periodic verification — gate-attainment per project class, exception-inventory current, lifecycle effectiveness (freshness=180; dev practices evolve)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.25:rev_date>>
_Why: 27002:8.25 — periodic_

<<TEXT>>

## 2. Reviewer identity (Engineering leads + InfoSec)

<<MUST item:A.8.25:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Gate-attainment trending per project class

<<MUST item:A.8.25:rev_gate_attainment>>
_Why: 27002:8.25 — applied_

<<TEXT>>

## 4. Exception inventory re-confirmed / retired

<<MUST item:A.8.25:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 5. Lifecycle-effectiveness review (incidents that traced to SDLC gaps)

<<MUST item:A.8.25:rev_lifecycle_effectiveness>>
_Why: Closes the loop_

<<TEXT>>

## 6. Findings propagated to policy / scope

<<MUST item:A.8.25:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.25:rev_next_date>>
_Why: Planning_

<<TEXT>>
