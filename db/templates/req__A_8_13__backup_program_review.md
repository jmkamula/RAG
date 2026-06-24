---
leaf_id: req:A.8.13:backup_program_review
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Backup Program Review

> Annual verification — restore-test attainment per RPO tier, scope completeness, encryption + immutability posture (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.13:rev_date>>
_Why: 27002:8.13 — periodic_

<<TEXT>>

## 2. Reviewer identity (Backup Operations + Infrastructure + InfoSec)

<<MUST item:A.8.13:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Restore-test attainment per tier (cadence met, RPO met)

<<MUST item:A.8.13:rev_test_attainment>>
_Why: 27002:8.13 — regularly tested_

<<TEXT>>

## 4. Scope-completeness check (new in-scope system covered)

<<MUST item:A.8.13:rev_scope_completeness>>
_Why: 27002:8.13 — maintained_

<<TEXT>>

## 5. Threat-posture review (ransomware-resilience: immutability / air-gap / 3-2-1 still adequate)

<<MUST item:A.8.13:rev_threat_posture>>
_Why: Modern resilience_

<<TEXT>>

## 6. Findings propagated to procedure / scope

<<MUST item:A.8.13:rev_procedure_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.13:rev_next_date>>
_Why: Planning_

<<TEXT>>
