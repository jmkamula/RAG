---
leaf_id: req:A.7.13:applicable_equipment_scope
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Equipment Maintenance Scope

> The upstream — which equipment classes require what maintenance cadence and what supervision level

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Equipment classes (drawn from A.7.8 + A.5.9 — servers, network gear, UPS/generator, HVAC, recording devices)

<<MUST item:A.7.13:scope_classes>>
_Why: 27002:7.13 — equipment_

<<TEXT>>

## 2. Cadence per class (vendor-recommended + risk-adjusted)

<<MUST item:A.7.13:scope_cadence_per_class>>
_Why: 27002:7.13 — maintained correctly_

<<TEXT>>

## 3. Supervision threshold (which equipment classes require in-house supervision during maintenance — typically anything carrying classified data)

<<MUST item:A.7.13:scope_supervision_threshold>>
_Why: 27002:7.13 — confidentiality_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new equipment class, refreshed hardware)

<<SHOULD item:A.7.13:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
