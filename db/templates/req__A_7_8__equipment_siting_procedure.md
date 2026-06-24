---
leaf_id: req:A.7.8:equipment_siting_procedure
control_ref: A.7.8
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Equipment Siting and Protection Procedure

> A.7.8 requires equipment to be sited securely and protected. The procedure documents siting principles, tamper-resistance, cable management, visibility minimisation. The equipment register, applicable-equipment scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Siting principles (away from public view, environmental controls, restricted access proportional to equipment class)

<<MUST item:A.7.8:siting_principles>>
_Why: 27002:7.8 — sited securely_

<<TEXT>>

## 2. Tamper-resistance / detection measures for sensitive equipment (HSMs, network gear, recording devices)

<<MUST item:A.7.8:tamper_resistance>>
_Why: 27002:7.8 — protected_

<<TEXT>>

## 3. Cable management to prevent damage or interception (cross-link to A.7.12 cabling security)

<<MUST item:A.7.8:cable_management>>
_Why: 27002:7.8 — protected_

<<TEXT>>

## 4. Visibility minimisation (screens not facing windows, no labels indicating contents, no public-facing maker/model info)

<<MUST item:A.7.8:visibility>>
_Why: 27002:7.8 — sited securely_

<<TEXT>>

## 5. Rules on food/drink near equipment (incidental-damage prevention)

<<MUST item:A.7.8:eating_drinking>>
_Why: Common cause of damage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Specific guidance for high-value equipment (HSMs, server racks, key safes — extra siting + tamper-detection requirements)

<<SHOULD item:A.7.8:hsm_specifics>>
_Why: Proportionality_

<<TEXT>>
