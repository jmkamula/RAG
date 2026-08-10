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

<<DOC_CONTROL>>

> A.8.20 requires networks + devices secured, managed, controlled. Policy states architecture principles, zone model, monitoring requirement, change-control linkage. Per-network register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you create a clear policy for securing and managing your networks and devices, outlining key principles, monitoring, and change-control requirements. It's designed to help you meet ISO 27001 program standards.

## When to use it

Use this template whenever your organization operates networks or connected devices, as it always applies to your environment. Review and update the policy whenever there are significant changes or as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting the required sections, plus additional time if you need to create or update a network register for your environment.

## 1. Security architecture principles (defence-in-depth / segmentation / fail-safe / zero-trust direction)

<<MUST item:A.8.20:architecture>>
_Why: 27002:8.20 — secured, managed and controlled_

<<GUIDANCE>>

<<TEXT>>

## 2. Perimeter + zone definitions (cross-link to A.8.22 segregation)

<<MUST item:A.8.20:zones>>
_Why: 27002:8.20 — controlled_

<<GUIDANCE>>

<<TEXT>>

## 3. Monitoring requirement (cross-link to A.8.16)

<<MUST item:A.8.20:monitoring_req>>
_Why: 27002:8.20 — controlled_

<<GUIDANCE>>

<<TEXT>>

## 4. Change control for network devices (cross-link to A.8.32)

<<MUST item:A.8.20:change_control>>
_Why: 27002:8.20 — managed_

<<GUIDANCE>>

<<TEXT>>

## 5. Zero-trust direction encoded — no implicit trust at network layer; identity-verified per request (modern baseline)

<<MUST item:A.8.20:zero_trust>>
_Why: Modern best practice (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

## 6. Named policy authority (Network Engineering lead with InfoSec lead)

<<MUST item:A.8.20:authority>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Network-as-code direction (repeatable deployments)

<<SHOULD item:A.8.20:network_as_code>>
_Why: Modern practice_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
