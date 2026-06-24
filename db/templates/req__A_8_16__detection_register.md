---
leaf_id: req:A.8.16:detection_register
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Detection Use-Case Register

> Catalogue of active detections — rule / use-case id, asset coverage, last-tuning date, true-positive rate, status

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-detection use-case identifier (rule id / hunt id / playbook id)

<<MUST item:A.8.16:reg_use_case_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-detection asset coverage (which asset classes / sources feed it)

<<MUST item:A.8.16:reg_coverage>>
_Why: 27002:8.16 — networks, systems, applications_

<<TEXT>>

## 3. Per-detection threat mapping (MITRE ATT&CK technique or equivalent)

<<MUST item:A.8.16:reg_threat_mapping>>
_Why: Coverage visibility_

<<TEXT>>

## 4. Per-detection true-positive rate (rolling window)

<<MUST item:A.8.16:reg_tp_rate>>
_Why: Detection effectiveness_

<<TEXT>>

## 5. Per-detection last-tuning date

<<MUST item:A.8.16:reg_last_tuned>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-detection named owner (detection engineer)

<<SHOULD item:A.8.16:reg_owner>>
_Why: Accountability_

<<TEXT>>
