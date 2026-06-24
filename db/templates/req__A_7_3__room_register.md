---
leaf_id: req:A.7.3:room_register
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Room Register

> The catalogue of rooms across all sites with classification, locking standard, occupancy controls, owner. Drives 'show me every room is classified and protected per its tier' audit

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-room unique identifier

<<MUST item:A.7.3:reg_room_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-room classification (matches procedure's classification scheme)

<<MUST item:A.7.3:reg_classification>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 3. Per-room locking standard in place (matches required standard per classification)

<<MUST item:A.7.3:reg_locking>>
_Why: 27002:7.3 — physical security_

<<TEXT>>

## 4. Per-room owner (department or named individual responsible)

<<MUST item:A.7.3:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Per-room last assessment date

<<MUST item:A.7.3:reg_last_assessed>>
_Why: 27002:7.3 — current_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Remediation log per row where locking falls short of required standard

<<SHOULD item:A.7.3:reg_remediation>>
_Why: Operational discipline_

<<TEXT>>
