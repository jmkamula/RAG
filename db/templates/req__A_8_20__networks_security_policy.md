---
leaf_id: req:A.8.20:networks_security_policy
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Networks Security Policy

> A.8.20 requires networks + devices secured, managed, controlled. Policy states architecture principles, zone model, monitoring requirement, change-control linkage. Per-network register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Security architecture principles (defence-in-depth / segmentation / fail-safe / zero-trust direction)

<<MUST item:A.8.20:architecture>>
_Why: 27002:8.20 — secured, managed and controlled_

<<TEXT>>

## 2. Perimeter + zone definitions (cross-link to A.8.22 segregation)

<<MUST item:A.8.20:zones>>
_Why: 27002:8.20 — controlled_

<<TEXT>>

## 3. Monitoring requirement (cross-link to A.8.16)

<<MUST item:A.8.20:monitoring_req>>
_Why: 27002:8.20 — controlled_

<<TEXT>>

## 4. Change control for network devices (cross-link to A.8.32)

<<MUST item:A.8.20:change_control>>
_Why: 27002:8.20 — managed_

<<TEXT>>

## 5. Zero-trust direction encoded — no implicit trust at network layer; identity-verified per request (modern baseline)

<<MUST item:A.8.20:zero_trust>>
_Why: Modern best practice (Style v2 promotion)_

<<TEXT>>

## 6. Named policy authority (Network Engineering lead with InfoSec lead)

<<MUST item:A.8.20:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Network-as-code direction (repeatable deployments)

<<SHOULD item:A.8.20:network_as_code>>
_Why: Modern practice_

<<TEXT>>
