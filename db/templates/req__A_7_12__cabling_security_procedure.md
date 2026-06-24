---
leaf_id: req:A.7.12:cabling_security_procedure
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Cabling Security Procedure

> A.7.12 requires cables carrying power, data, or supporting services to be protected from interception, interference, or damage. The procedure documents routing, separation, labelling, tamper-evidence, patch-panel security. The cabling register, applicable-runs scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Cable routing principles (conduits, protected paths, away from public areas)

<<MUST item:A.7.12:routing>>
_Why: 27002:7.12 — protected from damage_

<<TEXT>>

## 2. Separation of power and data cables to reduce interference

<<MUST item:A.7.12:separation>>
_Why: 27002:7.12 — interference_

<<TEXT>>

## 3. Cable and patch-panel labelling for traceability

<<MUST item:A.7.12:labelling>>
_Why: 27002:7.12 — protected_

<<TEXT>>

## 4. Tamper-evident protection where sensitive data is carried (locked cabinets, sealed runs)

<<MUST item:A.7.12:tamper_evidence>>
_Why: 27002:7.12 — interception_

<<TEXT>>

## 5. Patch panel / IDF / MDF physical security (locked rooms, access logged)

<<MUST item:A.7.12:patch_panel_security>>
_Why: 27002:7.12 — protected_

<<TEXT>>

## 6. Encrypted backbone or MACsec on segments crossing low-trust zones

<<MUST item:A.7.12:encrypted_backbone>>
_Why: Defense in depth_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic physical inspection schedule (drift prevention)

<<SHOULD item:A.7.12:periodic_inspection>>
_Why: Drift prevention_

<<TEXT>>
