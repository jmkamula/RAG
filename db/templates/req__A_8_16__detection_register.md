---
leaf_id: req:A.8.16:detection_register
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Detection Use-Case Register

<<DOC_CONTROL>>

> Catalogue of active detections — rule / use-case id, asset coverage, last-tuning date, true-positive rate, status

<!-- TABLE-COLUMNS leaf:req:A.8.16:detection_register -->
<!-- column: item:A.8.16:reg_use_case_id -->
<!-- column: item:A.8.16:reg_coverage -->
<!-- column: item:A.8.16:reg_threat_mapping -->
<!-- column: item:A.8.16:reg_tp_rate -->
<!-- column: item:A.8.16:reg_last_tuned -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an organized record of all your active detection rules, including important details like coverage, tuning history, and performance. It's useful for tracking and improving your security monitoring efforts.

## When to use it

Use this register whenever you need to document or review your detection use-cases, as it should always reflect your current environment. Update it as needed whenever new detections are added or existing ones are changed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each detection rule you document. Completing the register from scratch may take a few hours, depending on how many detection rules you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.16:detection_register -->
| Reg Use Case Id | Reg Coverage | Reg Threat Mapping | Reg Tp Rate | Reg Last Tuned |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.16:detection_register -->

## Column guidance — what to fill in

### Reg Use Case Id

<<MUST item:A.8.16:reg_use_case_id>>
_Why: Identification_

> _Standard text:_ Per-detection use-case identifier (rule id / hunt id / playbook id)

<<GUIDANCE>>

### Reg Coverage

<<MUST item:A.8.16:reg_coverage>>
_Why: 27002:8.16 — networks, systems, applications_

> _Standard text:_ Per-detection asset coverage (which asset classes / sources feed it)

<<GUIDANCE>>

### Reg Threat Mapping

<<MUST item:A.8.16:reg_threat_mapping>>
_Why: Coverage visibility_

> _Standard text:_ Per-detection threat mapping (MITRE ATT&CK technique or equivalent)

<<GUIDANCE>>

### Reg Tp Rate

<<MUST item:A.8.16:reg_tp_rate>>
_Why: Detection effectiveness_

> _Standard text:_ Per-detection true-positive rate (rolling window)

<<GUIDANCE>>

### Reg Last Tuned

<<MUST item:A.8.16:reg_last_tuned>>
_Why: Drift detection_

> _Standard text:_ Per-detection last-tuning date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.16:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-detection named owner (detection engineer)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
