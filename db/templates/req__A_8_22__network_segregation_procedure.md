---
leaf_id: req:A.8.22:network_segregation_procedure
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Network Segregation Procedure

> A.8.22 requires groups of services / users / systems segregated. Procedure documents zone model, inter-zone flow rules, enforcement, exception path. Per-zone register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Rationale for segregation (sensitivity / function / trust level / regulatory)

<<MUST item:A.8.22:rationale>>
_Why: 27002:8.22 — segregated_

<<TEXT>>

## 2. Zone model documented (DMZ / internal / restricted / OT / dev/test/prod / per-tenant where multi-tenant)

<<MUST item:A.8.22:zone_model>>
_Why: 27002:8.22 — groups segregated_

<<TEXT>>

## 3. Inter-zone flow rules — default-deny with explicit allowlist; bidirectionally documented

<<MUST item:A.8.22:flow_rules>>
_Why: 27002:8.22 — segregated_

<<TEXT>>

## 4. Enforcement points (firewall / ACL / security group / identity-aware proxy / service-mesh policy)

<<MUST item:A.8.22:enforcement>>
_Why: 27002:8.22 — segregated_

<<TEXT>>

## 5. Exception process for cross-zone access (time-bound + InfoSec-approved + logged)

<<MUST item:A.8.22:exception_path>>
_Why: Operational reality_

<<TEXT>>

## 6. Micro-segmentation direction for east-west traffic (modern baseline for high-criticality)

<<MUST item:A.8.22:micro_segmentation>>
_Why: Modern direction (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Network Engineering lead with InfoSec partner)

<<SHOULD item:A.8.22:owner>>
_Why: Accountability_

<<TEXT>>
