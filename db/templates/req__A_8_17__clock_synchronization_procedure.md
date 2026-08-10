---
leaf_id: req:A.8.17:clock_synchronization_procedure
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Clock Synchronization Procedure

<<DOC_CONTROL>>

> A.8.17 requires clocks synchronised to approved sources. Procedure names sources, protocol, scope, monitoring. Per-system sync register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document how your organization's clocks are synchronized with approved time sources, covering protocols, monitoring, and system scope. It's designed to support compliance with ISO 27001 control A.8.17.

## When to use it

Use this procedure whenever your environment requires clock synchronization to meet compliance standards, and update it whenever your synchronization methods or sources change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of systems you need to include in your synchronization register.

## 1. Approved time sources named (stratum-1 NTP / GPS / vendor-cloud time service)

<<MUST item:A.8.17:approved_sources>>
_Why: 27002:8.17 — approved time sources_

<<GUIDANCE>>

<<TEXT>>

## 2. Synchronisation protocol (NTP / PTP) with security where supported (NTS / authenticated NTP)

<<MUST item:A.8.17:protocol>>
_Why: 27002:8.17 — synchronized_

<<GUIDANCE>>

<<TEXT>>

## 3. Scope (servers / network devices / endpoints / containers / cloud services / OT)

<<MUST item:A.8.17:scope>>
_Why: 27002:8.17 — information processing systems_

<<GUIDANCE>>

<<TEXT>>

## 4. Sync-status monitoring (drift threshold + alert on source loss + alert on stratum increase)

<<MUST item:A.8.17:monitoring>>
_Why: 27002:8.17 — synchronized_

<<GUIDANCE>>

<<TEXT>>

## 5. Stratum hierarchy documented (internal stratum-2 distribution from external stratum-1)

<<MUST item:A.8.17:stratum_hierarchy>>
_Why: Topology clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. NTP-feed security (authenticated / signed) for high-criticality logging contexts

<<SHOULD item:A.8.17:source_security>>
_Why: Defence in depth_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
