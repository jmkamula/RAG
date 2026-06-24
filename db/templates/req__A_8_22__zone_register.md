---
leaf_id: req:A.8.22:zone_register
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Network Zone Register

> Per-zone catalogue — zone id, classification, contained systems, enforcement boundary, owner

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-zone unique identifier

<<MUST item:A.8.22:reg_zone_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-zone classification tier

<<MUST item:A.8.22:reg_classification>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-zone contained-systems list (drawn from A.5.9)

<<MUST item:A.8.22:reg_contained_systems>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Per-zone enforcement-boundary description (specific firewall / ACL / policy)

<<MUST item:A.8.22:reg_enforcement>>
_Why: 27002:8.22 — segregated_

<<TEXT>>

## 5. Per-zone exception inventory (cross-zone allowances with expiry)

<<MUST item:A.8.22:reg_exceptions>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-zone named owner

<<SHOULD item:A.8.22:reg_owner>>
_Why: Accountability_

<<TEXT>>
