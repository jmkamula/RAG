---
leaf_id: req:A.7.8:applicable_equipment_scope
control_ref: A.7.8
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Equipment Scope

> The upstream — which equipment classes are in scope and what drives the protection level per class

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Equipment classes (workstations, server-room equipment, network kit, HSMs, recording devices, printers/MFDs)

<<MUST item:A.7.8:scope_classes>>
_Why: 27002:7.8 — equipment_

<<TEXT>>

## 2. Protection tier per class (basic / standard / high / critical)

<<MUST item:A.7.8:scope_protection_tiers>>
_Why: 27002:7.8 — proportional_

<<TEXT>>

## 3. Exclusions stated (off-premises equipment → A.7.9; ephemeral cloud — no physical footprint)

<<MUST item:A.7.8:scope_exclusions>>
_Why: 27002:7.8 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new equipment class, hardware refresh, M&A)

<<SHOULD item:A.7.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
