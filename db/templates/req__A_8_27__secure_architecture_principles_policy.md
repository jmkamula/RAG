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

> A.8.27 requires principles established, documented, maintained, applied. Policy enumerates principles + application context + maintenance approach. Reference-architecture register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Principles enumerated (defence-in-depth / least-privilege / fail-safe-defaults / separation-of-concerns / complete-mediation / zero-trust direction)

<<MUST item:A.8.27:principles>>
_Why: 27002:8.27 — principles established_

<<TEXT>>

## 2. Application to development activities defined (per principle, what it means in design / code / deployment)

<<MUST item:A.8.27:application>>
_Why: 27002:8.27 — applied to development activities_

<<TEXT>>

## 3. Principles documented in accessible form for engineers (wiki / handbook / training material)

<<MUST item:A.8.27:documented>>
_Why: 27002:8.27 — documented_

<<TEXT>>

## 4. Maintenance cadence + responsibility (review as technologies / threats / regulations evolve)

<<MUST item:A.8.27:maintenance>>
_Why: 27002:8.27 — maintained_

<<TEXT>>

## 5. Threat-modelling methodology integration (cross-link to A.8.26 + design-phase practice)

<<MUST item:A.8.27:tm_integration>>
_Why: Closes design loop (Style v2 promotion)_

<<TEXT>>

## 6. Named policy authority (Chief Architect / Security Architect with InfoSec lead)

<<MUST item:A.8.27:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Reference architecture patterns embedding the principles (concrete blueprints)

<<SHOULD item:A.8.27:reference_arch>>
_Why: Concrete guidance_

<<TEXT>>
