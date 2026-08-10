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

<<DOC_CONTROL>>

> The upstream — which equipment classes require what maintenance cadence and what supervision level

## What this template gives you

This template helps you clearly define which types of equipment in your environment need regular maintenance, how often they should be serviced, and what level of oversight is required.

## When to use it

Use this document whenever you need to outline or update the maintenance requirements for equipment in your environment. Review and refresh it whenever there are changes to your equipment or maintenance procedures.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements with thoughtful detail.

## 1. Equipment classes (drawn from A.7.8 + A.5.9 — servers, network gear, UPS/generator, HVAC, recording devices)

<<MUST item:A.7.13:scope_classes>>
_Why: 27002:7.13 — equipment_

<<GUIDANCE>>

<<TEXT>>

## 2. Cadence per class (vendor-recommended + risk-adjusted)

<<MUST item:A.7.13:scope_cadence_per_class>>
_Why: 27002:7.13 — maintained correctly_

<<GUIDANCE>>

<<TEXT>>

## 3. Supervision threshold (which equipment classes require in-house supervision during maintenance — typically anything carrying classified data)

<<MUST item:A.7.13:scope_supervision_threshold>>
_Why: 27002:7.13 — confidentiality_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new equipment class, refreshed hardware)

<<SHOULD item:A.7.13:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
