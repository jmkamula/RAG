---
leaf_id: req:A.8.25:project_register
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Development Project Register

> Per-project SDLC compliance — project id, lifecycle stage, security-checkpoint status, owner

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-project unique identifier (cross-link to A.5.8 project register)

<<MUST item:A.8.25:reg_project_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-project current lifecycle stage (initiation / design / build / test / release / operate)

<<MUST item:A.8.25:reg_lifecycle_stage>>
_Why: 27002:8.25 — secure development_

<<TEXT>>

## 3. Per-project security-checkpoint status (which gates passed)

<<MUST item:A.8.25:reg_checkpoint_status>>
_Why: 27002:8.25 — applied_

<<TEXT>>

## 4. Per-project named owner (technical lead with security partner)

<<MUST item:A.8.25:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Per-project data classification footprint (drives PII-handling rules)

<<MUST item:A.8.25:reg_data_classification>>
_Why: GDPR alignment_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-project exception log (waived gates with rationale + compensating controls)

<<SHOULD item:A.8.25:reg_exception_log>>
_Why: Defensibility_

<<TEXT>>
