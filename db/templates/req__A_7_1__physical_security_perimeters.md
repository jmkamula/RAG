---
leaf_id: req:A.7.1:physical_security_perimeters
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Physical Security Perimeters Policy

> A.7.1 requires security perimeters to be defined and used to protect areas containing information and associated assets. The policy defines perimeter types, area classification, barrier types, access points. The perimeter register, applicable-sites scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Inventory of perimeters defined (which physical boundaries exist per site)

<<MUST item:A.7.1:perimeter_inventory>>
_Why: 27002:7.1 — security perimeters defined_

<<TEXT>>

## 2. Classification of areas inside each perimeter (general office, secure area, server room, restricted)

<<MUST item:A.7.1:area_classification>>
_Why: 27002:7.1 — protect areas_

<<TEXT>>

## 3. Barrier types per perimeter class (walls, fences, locked doors, mantraps, anti-ramming where critical)

<<MUST item:A.7.1:barrier_types>>
_Why: 27002:7.1 — used to protect_

<<TEXT>>

## 4. Access points designated per perimeter (which doors are entry/exit, which are emergency-only)

<<MUST item:A.7.1:access_points>>
_Why: 27002:7.1 — defined_

<<TEXT>>

## 5. Owner named for physical security at each site (Facilities lead with InfoSec partner)

<<MUST item:A.7.1:owner>>
_Why: Accountability_

<<TEXT>>

## 6. Integration with logical access (which logical privileges require entry to which perimeter — cross-link to A.5.18 access rights)

<<MUST item:A.7.1:logical_integration>>
_Why: Cross-domain consistency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Floor plans or perimeter drawings referenced

<<SHOULD item:A.7.1:drawings>>
_Why: Audit clarity_

<<TEXT>>

### 2. Shared-building considerations (other tenants, common corridors, lobby access)

<<SHOULD item:A.7.1:shared_building>>
_Why: Common real-world setup_

<<TEXT>>
