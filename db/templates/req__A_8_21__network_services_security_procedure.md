---
leaf_id: req:A.8.21:network_services_security_procedure
control_ref: A.8.21
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Security of Network Services Procedure

<<DOC_CONTROL>>

> A.8.21 requires security mechanisms, service levels, requirements identified, implemented, monitored. Procedure documents the assessment approach, security-mechanism standards, SLA monitoring. Per-service register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document how your organization secures its network services, including how you assess risks, set security standards, and monitor service levels. It provides a clear structure for tracking your approach and compliance.

## When to use it

Use this procedure whenever your environment includes network services that need to be secured and monitored. Update it as needed to reflect changes in your services or security requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of network services you need to register and the detail required for each section.

## 1. Security-mechanism standards per service class (encryption / authentication / integrity / availability) with minimum baselines

<<MUST item:A.8.21:security_mechanisms>>
_Why: 27002:8.21 — security mechanisms_

<<GUIDANCE>>

<<TEXT>>

## 2. SLA baseline expectations per service class (availability / latency / support response)

<<MUST item:A.8.21:sla_baseline>>
_Why: 27002:8.21 — service levels_

<<GUIDANCE>>

<<TEXT>>

## 3. Service-delivery monitoring approach (synthetic checks / passive instrumentation / vendor-reported)

<<MUST item:A.8.21:monitoring_approach>>
_Why: 27002:8.21 — monitored_

<<GUIDANCE>>

<<TEXT>>

## 4. Vendor-managed services governance (cross-link to A.5.19 + A.5.20 + A.5.22 supplier review)

<<MUST item:A.8.21:vendor_governance>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 5. Incident path when service degraded / breached (cross-link to A.5.25/A.5.26)

<<MUST item:A.8.21:incident_path>>
_Why: Operational discipline_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Network Engineering lead with Supplier Management partner)

<<SHOULD item:A.8.21:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
