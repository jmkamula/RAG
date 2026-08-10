---
leaf_id: req:A.8.21:service_register
control_ref: A.8.21
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Network Services Register

<<DOC_CONTROL>>

> Per-service catalogue — service id, provider, security mechanisms in use, SLA performance, last-review date

<!-- TABLE-COLUMNS leaf:req:A.8.21:service_register -->
<!-- column: item:A.8.21:reg_service_id -->
<!-- column: item:A.8.21:reg_provider -->
<!-- column: item:A.8.21:reg_mechanisms -->
<!-- column: item:A.8.21:reg_sla_performance -->
<!-- column: item:A.8.21:reg_last_reviewed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your network services, including details like provider, security measures, and service performance. It’s useful for tracking and reviewing your network services in one place.

## When to use it

Use this register whenever you need to document or update information about your network services, and refresh it whenever there are changes or during regular reviews to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each service you list. Completing the register from scratch for a handful of services may take 1-2 hours, depending on how many you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.21:service_register -->
| Reg Service Id | Reg Provider | Reg Mechanisms | Reg Sla Performance | Reg Last Reviewed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.21:service_register -->

## Column guidance — what to fill in

### Reg Service Id

<<MUST item:A.8.21:reg_service_id>>
_Why: Identification_

> _Standard text:_ Per-row service identifier (ISP / CDN / DNS / SD-WAN / managed-firewall)

<<GUIDANCE>>

### Reg Provider

<<MUST item:A.8.21:reg_provider>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row provider + contract reference (cross-link to A.5.19/A.5.20 supplier register)

<<GUIDANCE>>

### Reg Mechanisms

<<MUST item:A.8.21:reg_mechanisms>>
_Why: 27002:8.21 — security mechanisms_

> _Standard text:_ Per-row security mechanisms in use (matches procedure's baseline for the class)

<<GUIDANCE>>

### Reg Sla Performance

<<MUST item:A.8.21:reg_sla_performance>>
_Why: 27002:8.21 — monitored_

> _Standard text:_ Per-row SLA performance vs baseline

<<GUIDANCE>>

### Reg Last Reviewed

<<MUST item:A.8.21:reg_last_reviewed>>
_Why: Drift detection_

> _Standard text:_ Per-row last-review timestamp

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.21:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row owner (relationship manager + technical owner)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
