---
leaf_id: req:A.8.27:secure_architecture_principles_policy
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Secure System Architecture and Engineering Principles Policy

<<DOC_CONTROL>>

> A.8.27 requires principles established, documented, maintained, applied. Policy enumerates principles + application context + maintenance approach. Reference-architecture register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you clearly define and document the security principles that guide your system architecture and engineering practices. It ensures your approach is consistent, well-maintained, and aligned with ISO 27001 requirements.

## When to use it

Use this template when your organization needs to establish or update its secure system architecture principles, especially if your risk profile or regulatory obligations change. Review and refresh the policy as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this policy from scratch, depending on how many principles and context details you need to include.

## 1. Principles enumerated (defence-in-depth / least-privilege / fail-safe-defaults / separation-of-concerns / complete-mediation / zero-trust direction)

<<MUST item:A.8.27:principles>>
_Why: 27002:8.27 — principles established_

<<GUIDANCE>>

<<TEXT>>

## 2. Application to development activities defined (per principle, what it means in design / code / deployment)

<<MUST item:A.8.27:application>>
_Why: 27002:8.27 — applied to development activities_

<<GUIDANCE>>

<<TEXT>>

## 3. Principles documented in accessible form for engineers (wiki / handbook / training material)

<<MUST item:A.8.27:documented>>
_Why: 27002:8.27 — documented_

<<GUIDANCE>>

<<TEXT>>

## 4. Maintenance cadence + responsibility (review as technologies / threats / regulations evolve)

<<MUST item:A.8.27:maintenance>>
_Why: 27002:8.27 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 5. Threat-modelling methodology integration (cross-link to A.8.26 + design-phase practice)

<<MUST item:A.8.27:tm_integration>>
_Why: Closes design loop (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

## 6. Named policy authority (Chief Architect / Security Architect with InfoSec lead)

<<MUST item:A.8.27:authority>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Reference architecture patterns embedding the principles (concrete blueprints)

<<SHOULD item:A.8.27:reference_arch>>
_Why: Concrete guidance_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
