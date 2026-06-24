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

> A.7.3 requires physical security to be designed and implemented for offices, rooms, and facilities. The procedure documents room classification, locking, signage, key/card management, and occupancy. The room register, applicable-rooms scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Classification of rooms (general, restricted, secure, high-security)

<<MUST item:A.7.3:room_classification>>
_Why: 27002:7.3 — designed and implemented_

<<TEXT>>

## 2. Locking standards per classification (mechanical, electronic with audit logging, biometric for high-security)

<<MUST item:A.7.3:locking_standards>>
_Why: 27002:7.3 — physical security_

<<TEXT>>

## 3. Signage and visibility minimisation (no advertising of sensitive areas; minimum signage on doors)

<<MUST item:A.7.3:signage>>
_Why: 27002:7.3 — designed_

<<TEXT>>

## 4. Key/card lifecycle management (issue, return, lost-card revocation; cross-link to A.5.18)

<<MUST item:A.7.3:key_management>>
_Why: 27002:7.3 — implemented_

<<TEXT>>

## 5. Occupancy controls (max people in secure rooms, lone-worker rules where required)

<<MUST item:A.7.3:occupancy_controls>>
_Why: 27002:7.3 — designed_

<<TEXT>>

## 6. Fit-out / construction security requirements (walls to slab, no gaps above ceiling, sound insulation where speech-confidential)

<<MUST item:A.7.3:fit_out>>
_Why: Often overlooked_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Shared-building considerations (other tenants, common corridors, cleaning-staff access)

<<SHOULD item:A.7.3:shared_building>>
_Why: Common setup_

<<TEXT>>
