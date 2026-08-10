---
leaf_id: req:A.8.14:redundancy_baseline
control_ref: A.8.14
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Redundancy Baseline

<<DOC_CONTROL>>

> A.8.14 baseline — critical services identified, availability requirements per service, redundancy approach per service. Procedure (failover), failover-test register, review are sibling leaves

## What this template gives you

This template helps you document which critical services need to stay available, what their uptime requirements are, and how you ensure redundancy for each one. It also covers how you handle failovers and keep track of related tests.

## When to use it

Use this template whenever you need to define or review your organization's approach to service redundancy and availability. Update it whenever your environment changes or when you add or change critical services.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of services and failover tests you need to document.

## 1. Critical services enumerated with availability requirement per service (drawn from A.5.30 BIA)

<<MUST item:A.8.14:bl_critical_services>>
_Why: 27002:8.14 — availability requirements_

<<GUIDANCE>>

<<TEXT>>

## 2. Redundancy approach per service (active-active / active-passive / cold-standby / multi-region)

<<MUST item:A.8.14:bl_redundancy_approach>>
_Why: 27002:8.14 — redundancy sufficient_

<<GUIDANCE>>

<<TEXT>>

## 3. Monitoring of redundant components — failures detected before failover need (no silent single-point loss)

<<MUST item:A.8.14:bl_monitoring>>
_Why: 27002:8.14 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 4. Cross-AZ / cross-region distribution for cloud-hosted services (modern baseline; single-AZ insufficient)

<<MUST item:A.8.14:bl_cross_az>>
_Why: Modern hosting reality_

<<GUIDANCE>>

<<TEXT>>

## 5. SLA implications documented (what tenants are promised — honest about redundant vs single-instance)

<<MUST item:A.8.14:bl_sla_implications>>
_Why: Honest commitment_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Chaos-engineering / fault-injection practice for high-criticality services

<<SHOULD item:A.8.14:bl_chaos_engineering>>
_Why: Modern resilience_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
