---
leaf_id: req:A.8.11:masking_program_review
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Masking Program Review

> Annual verification — masking effectiveness (re-identification residual-risk samples), register currency, exception inventory reviewed (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.11:rev_date>>
_Why: 27002:8.11 — periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + Data Engineering + InfoSec)

<<MUST item:A.8.11:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Re-identification residual-risk sampling outcome (acceptable or technique upgrade required)

<<MUST item:A.8.11:rev_effectiveness>>
_Why: 27002:8.11 — effective_

<<TEXT>>

## 4. Register currency check (refresh timestamps within tolerance)

<<MUST item:A.8.11:rev_register_currency>>
_Why: Drift prevention_

<<TEXT>>

## 5. Exception inventory re-confirmed / retired

<<MUST item:A.8.11:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 6. Findings propagated to procedure / approved-techniques list

<<MUST item:A.8.11:rev_procedure_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.11:rev_next_date>>
_Why: Planning_

<<TEXT>>
