---
leaf_id: req:A.8.26:application_register
control_ref: A.8.26
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Application Security Requirements Register

> Per-application catalogue — application id, requirements set applied, approval lineage, traceability status

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row application identifier

<<MUST item:A.8.26:reg_app_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row requirements set applied (which categories from the procedure)

<<MUST item:A.8.26:reg_requirements_set>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 3. Per-row approval lineage (who approved + when)

<<MUST item:A.8.26:reg_approval>>
_Why: Accountability_

<<TEXT>>

## 4. Per-row traceability status (requirements-to-test-cases coverage %)

<<MUST item:A.8.26:reg_traceability_status>>
_Why: 27002:8.26 — specified_

<<TEXT>>

## 5. Per-row data-classification footprint

<<MUST item:A.8.26:reg_classification>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row threat-model reference (link to artefact)

<<SHOULD item:A.8.26:reg_threat_model_ref>>
_Why: Defensibility_

<<TEXT>>
