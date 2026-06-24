---
leaf_id: req:A.7.12:cabling_program_review
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Cabling Program Review

> Annual verification of inspection completeness, register currency, remediation closure. Freshness=365

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.12:rev_date>>
_Why: 27002:7.12 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + Network lead + InfoSec)

<<MUST item:A.7.12:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-run inspection coverage in period (all runs inspected per planned cadence)

<<MUST item:A.7.12:rev_inspection_coverage>>
_Why: Drift prevention_

<<TEXT>>

## 4. Remediation closure rate from prior period

<<MUST item:A.7.12:rev_remediation_closure>>
_Why: Operational discipline_

<<TEXT>>

## 5. Changes propagated to the register / procedure

<<MUST item:A.7.12:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.12:rev_next_date>>
_Why: Planning_

<<TEXT>>
