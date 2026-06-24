---
leaf_id: req:A.8.22:segregation_program_review
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Network Segregation Program Review

> Annual verification — zone-register completeness, exception inventory current, flow-rules still appropriate, enforcement coverage verified (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.22:rev_date>>
_Why: 27002:8.22 — periodic_

<<TEXT>>

## 2. Reviewer identity (Network Engineering + InfoSec + Application Engineering leads)

<<MUST item:A.8.22:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register-completeness check (new zones registered)

<<MUST item:A.8.22:rev_register_completeness>>
_Why: Drift prevention_

<<TEXT>>

## 4. Exception inventory re-confirmed / retired

<<MUST item:A.8.22:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 5. Sample-based enforcement-coverage verification (configured rules match register)

<<MUST item:A.8.22:rev_enforcement_coverage>>
_Why: 27002:8.22 — segregated_

<<TEXT>>

## 6. Findings propagated to procedure / register

<<MUST item:A.8.22:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.22:rev_next_date>>
_Why: Planning_

<<TEXT>>
