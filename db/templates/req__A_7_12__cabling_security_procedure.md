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

<<DOC_CONTROL>>

> A.7.12 requires cables carrying power, data, or supporting services to be protected from interception, interference, or damage. The procedure documents routing, separation, labelling, tamper-evidence, patch-panel security. The cabling register, applicable-runs scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how your organization protects cabling for power, data, and services from interception, interference, or damage. It covers routing, separation, labeling, tamper-evidence, and patch-panel security, supporting compliance with ISO 27001 requirements.

## When to use it

Use this procedure whenever your environment includes cabling that needs protection, and update it whenever there are changes to your cabling or security practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this template from scratch, depending on the complexity of your cabling setup and the number of cable runs you need to document.

## 1. Cable routing principles (conduits, protected paths, away from public areas)

<<MUST item:A.7.12:routing>>
_Why: 27002:7.12 — protected from damage_

<<GUIDANCE>>

<<TEXT>>

## 2. Separation of power and data cables to reduce interference

<<MUST item:A.7.12:separation>>
_Why: 27002:7.12 — interference_

<<GUIDANCE>>

<<TEXT>>

## 3. Cable and patch-panel labelling for traceability

<<MUST item:A.7.12:labelling>>
_Why: 27002:7.12 — protected_

<<GUIDANCE>>

<<TEXT>>

## 4. Tamper-evident protection where sensitive data is carried (locked cabinets, sealed runs)

<<MUST item:A.7.12:tamper_evidence>>
_Why: 27002:7.12 — interception_

<<GUIDANCE>>

<<TEXT>>

## 5. Patch panel / IDF / MDF physical security (locked rooms, access logged)

<<MUST item:A.7.12:patch_panel_security>>
_Why: 27002:7.12 — protected_

<<GUIDANCE>>

<<TEXT>>

## 6. Encrypted backbone or MACsec on segments crossing low-trust zones

<<MUST item:A.7.12:encrypted_backbone>>
_Why: Defense in depth_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic physical inspection schedule (drift prevention)

<<SHOULD item:A.7.12:periodic_inspection>>
_Why: Drift prevention_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
