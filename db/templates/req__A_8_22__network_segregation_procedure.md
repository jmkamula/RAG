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

<<DOC_CONTROL>>

> A.8.22 requires groups of services / users / systems segregated. Procedure documents zone model, inter-zone flow rules, enforcement, exception path. Per-zone register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document how your network is divided into zones, how traffic is controlled between them, and how exceptions are managed. It ensures you meet ISO 27001 requirements for network segregation and provides a clear procedure for your team.

## When to use it

Use this template whenever your environment includes multiple groups of services, users, or systems that need to be separated for security. Update the document whenever your network changes or when you review your security program.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this template from scratch, depending on the complexity of your network and the number of zones you need to describe.

## 1. Rationale for segregation (sensitivity / function / trust level / regulatory)

<<MUST item:A.8.22:rationale>>
_Why: 27002:8.22 — segregated_

<<GUIDANCE>>

<<TEXT>>

## 2. Zone model documented (DMZ / internal / restricted / OT / dev/test/prod / per-tenant where multi-tenant)

<<MUST item:A.8.22:zone_model>>
_Why: 27002:8.22 — groups segregated_

<<GUIDANCE>>

<<TEXT>>

## 3. Inter-zone flow rules — default-deny with explicit allowlist; bidirectionally documented

<<MUST item:A.8.22:flow_rules>>
_Why: 27002:8.22 — segregated_

<<GUIDANCE>>

<<TEXT>>

## 4. Enforcement points (firewall / ACL / security group / identity-aware proxy / service-mesh policy)

<<MUST item:A.8.22:enforcement>>
_Why: 27002:8.22 — segregated_

<<GUIDANCE>>

<<TEXT>>

## 5. Exception process for cross-zone access (time-bound + InfoSec-approved + logged)

<<MUST item:A.8.22:exception_path>>
_Why: Operational reality_

<<GUIDANCE>>

<<TEXT>>

## 6. Micro-segmentation direction for east-west traffic (modern baseline for high-criticality)

<<MUST item:A.8.22:micro_segmentation>>
_Why: Modern direction (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Network Engineering lead with InfoSec partner)

<<SHOULD item:A.8.22:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
