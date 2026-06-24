---
leaf_id: req:A.8.1:endpoint_program_review
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Endpoint Program Review

> Annual verification that endpoint protections still match the policy, the register reflects reality, and any new device classes have been incorporated (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.1:rev_date>>
_Why: 27002:8.1 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT lead + InfoSec lead jointly)

<<MUST item:A.8.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Sample-based compliance verification across the register (encryption / patching / EDR coverage)

<<MUST item:A.8.1:rev_compliance_sample>>
_Why: Continuous evidence_

<<TEXT>>

## 4. Cross-check against the applicable scope — any new class or vendor missing

<<MUST item:A.8.1:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Changes propagated to the policy / register

<<MUST item:A.8.1:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
