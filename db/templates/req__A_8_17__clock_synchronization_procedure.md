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

> A.8.17 requires clocks synchronised to approved sources. Procedure names sources, protocol, scope, monitoring. Per-system sync register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Approved time sources named (stratum-1 NTP / GPS / vendor-cloud time service)

<<MUST item:A.8.17:approved_sources>>
_Why: 27002:8.17 — approved time sources_

<<TEXT>>

## 2. Synchronisation protocol (NTP / PTP) with security where supported (NTS / authenticated NTP)

<<MUST item:A.8.17:protocol>>
_Why: 27002:8.17 — synchronized_

<<TEXT>>

## 3. Scope (servers / network devices / endpoints / containers / cloud services / OT)

<<MUST item:A.8.17:scope>>
_Why: 27002:8.17 — information processing systems_

<<TEXT>>

## 4. Sync-status monitoring (drift threshold + alert on source loss + alert on stratum increase)

<<MUST item:A.8.17:monitoring>>
_Why: 27002:8.17 — synchronized_

<<TEXT>>

## 5. Stratum hierarchy documented (internal stratum-2 distribution from external stratum-1)

<<MUST item:A.8.17:stratum_hierarchy>>
_Why: Topology clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. NTP-feed security (authenticated / signed) for high-criticality logging contexts

<<SHOULD item:A.8.17:source_security>>
_Why: Defence in depth_

<<TEXT>>
