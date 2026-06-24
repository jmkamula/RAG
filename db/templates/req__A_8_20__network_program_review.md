---
leaf_id: req:A.8.20:network_program_review
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Network Program Review

> Annual architecture review — zone model still appropriate, register reflects reality, monitoring covers all in-scope segments (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.20:rev_date>>
_Why: 27002:8.20 — periodic_

<<TEXT>>

## 2. Reviewer identity (Network Engineering + InfoSec)

<<MUST item:A.8.20:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Architecture review — zone model still matches threat landscape + business reality

<<MUST item:A.8.20:rev_architecture>>
_Why: 27002:8.20 — managed_

<<TEXT>>

## 4. Register-completeness check (every new segment registered)

<<MUST item:A.8.20:rev_register_completeness>>
_Why: Drift prevention_

<<TEXT>>

## 5. Findings propagated to policy / register / scope

<<MUST item:A.8.20:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.20:rev_next_date>>
_Why: Planning_

<<TEXT>>
