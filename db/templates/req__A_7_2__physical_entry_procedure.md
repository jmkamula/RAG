---
leaf_id: req:A.7.2:physical_entry_procedure
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Physical Entry Controls Procedure

<<DOC_CONTROL>>

> A.7.2 requires secure areas to be protected by appropriate entry controls and access points. The procedure documents authorisation, entry mechanisms, visitor handling, deliveries, emergency egress, and periodic review. The entry register, applicable-areas scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how you control physical access to secure areas, including how you authorize entry, manage visitors and deliveries, and handle emergencies. It's designed to help you meet ISO 27001 requirements for physical entry controls.

## When to use it

Use this procedure whenever you need to define or update how people access secure areas in your organization. Review and refresh the document as needed to keep it accurate and effective.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this from scratch, depending on the complexity of your environment and the number of areas and entry points you need to cover.

## 1. Authorisation list per secure area (who is permitted, by role or name; cross-link to A.5.18)

<<MUST item:A.7.2:authorisation_list>>
_Why: 27002:7.2 — entry controls_

<<GUIDANCE>>

<<TEXT>>

## 2. Entry mechanism stated per area (badge, biometric, mechanical key, mantrap)

<<MUST item:A.7.2:entry_mechanism>>
_Why: 27002:7.2 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 3. Visitor handling (escort requirement, sign-in log, temporary badge, host accountability)

<<MUST item:A.7.2:visitor_process>>
_Why: 27002:7.2 — access points_

<<GUIDANCE>>

<<TEXT>>

## 4. Delivery / loading area handling (drop zones, no direct access to secure areas)

<<MUST item:A.7.2:deliveries>>
_Why: 27002:7.2 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 5. Emergency egress provisions (panic bars, post-incident accountability)

<<MUST item:A.7.2:emergency_egress>>
_Why: Life safety_

<<GUIDANCE>>

<<TEXT>>

## 6. Periodic access-list review trigger (links to A.5.18 access reviews)

<<MUST item:A.7.2:periodic_review>>
_Why: Drift prevention_

<<GUIDANCE>>

<<TEXT>>

## 7. Anti-tailgating measures (mantraps, awareness, observed entry, badge-back-in enforcement)

<<MUST item:A.7.2:tailgating>>
_Why: Common attack vector_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception handling process for one-off access needs

<<SHOULD item:A.7.2:exception>>
_Why: Operational flexibility_

<<GUIDANCE>>

<<TEXT>>

### 2. Named owner of the procedure (Facilities lead with InfoSec partner)

<<SHOULD item:A.7.2:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
