---
leaf_id: req:A.7.3:offices_rooms_facilities_procedure
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Securing Offices, Rooms and Facilities Procedure

<<DOC_CONTROL>>

> A.7.3 requires physical security to be designed and implemented for offices, rooms, and facilities. The procedure documents room classification, locking, signage, key/card management, and occupancy. The room register, applicable-rooms scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how your offices, rooms, and facilities are physically secured, including how you classify spaces, manage keys or cards, and keep track of who has access.

## When to use it

Use this procedure whenever you need to show that your physical spaces are protected, and update it whenever there are changes to your rooms, access methods, or occupancy.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of rooms and how detailed your access and key management processes are.

## 1. Classification of rooms (general, restricted, secure, high-security)

<<MUST item:A.7.3:room_classification>>
_Why: 27002:7.3 — designed and implemented_

<<GUIDANCE>>

<<TEXT>>

## 2. Locking standards per classification (mechanical, electronic with audit logging, biometric for high-security)

<<MUST item:A.7.3:locking_standards>>
_Why: 27002:7.3 — physical security_

<<GUIDANCE>>

<<TEXT>>

## 3. Signage and visibility minimisation (no advertising of sensitive areas; minimum signage on doors)

<<MUST item:A.7.3:signage>>
_Why: 27002:7.3 — designed_

<<GUIDANCE>>

<<TEXT>>

## 4. Key/card lifecycle management (issue, return, lost-card revocation; cross-link to A.5.18)

<<MUST item:A.7.3:key_management>>
_Why: 27002:7.3 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 5. Occupancy controls (max people in secure rooms, lone-worker rules where required)

<<MUST item:A.7.3:occupancy_controls>>
_Why: 27002:7.3 — designed_

<<GUIDANCE>>

<<TEXT>>

## 6. Fit-out / construction security requirements (walls to slab, no gaps above ceiling, sound insulation where speech-confidential)

<<MUST item:A.7.3:fit_out>>
_Why: Often overlooked_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Shared-building considerations (other tenants, common corridors, cleaning-staff access)

<<SHOULD item:A.7.3:shared_building>>
_Why: Common setup_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
