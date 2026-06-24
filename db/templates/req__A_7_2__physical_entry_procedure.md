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

> A.7.2 requires secure areas to be protected by appropriate entry controls and access points. The procedure documents authorisation, entry mechanisms, visitor handling, deliveries, emergency egress, and periodic review. The entry register, applicable-areas scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Authorisation list per secure area (who is permitted, by role or name; cross-link to A.5.18)

<<MUST item:A.7.2:authorisation_list>>
_Why: 27002:7.2 — entry controls_

<<TEXT>>

## 2. Entry mechanism stated per area (badge, biometric, mechanical key, mantrap)

<<MUST item:A.7.2:entry_mechanism>>
_Why: 27002:7.2 — appropriate_

<<TEXT>>

## 3. Visitor handling (escort requirement, sign-in log, temporary badge, host accountability)

<<MUST item:A.7.2:visitor_process>>
_Why: 27002:7.2 — access points_

<<TEXT>>

## 4. Delivery / loading area handling (drop zones, no direct access to secure areas)

<<MUST item:A.7.2:deliveries>>
_Why: 27002:7.2 — appropriate_

<<TEXT>>

## 5. Emergency egress provisions (panic bars, post-incident accountability)

<<MUST item:A.7.2:emergency_egress>>
_Why: Life safety_

<<TEXT>>

## 6. Periodic access-list review trigger (links to A.5.18 access reviews)

<<MUST item:A.7.2:periodic_review>>
_Why: Drift prevention_

<<TEXT>>

## 7. Anti-tailgating measures (mantraps, awareness, observed entry, badge-back-in enforcement)

<<MUST item:A.7.2:tailgating>>
_Why: Common attack vector_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception handling process for one-off access needs

<<SHOULD item:A.7.2:exception>>
_Why: Operational flexibility_

<<TEXT>>

### 2. Named owner of the procedure (Facilities lead with InfoSec partner)

<<SHOULD item:A.7.2:owner>>
_Why: Accountability_

<<TEXT>>
