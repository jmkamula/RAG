---
leaf_id: req:A.8.21:applicable_service_scope
control_ref: A.8.21
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Network Services Scope

<<DOC_CONTROL>>

> Upstream — what counts as 'network service' for A.8.21. ISP / CDN / DNS / SD-WAN / cloud connectivity / managed-firewall / VPN-as-service all in scope

## What this template gives you

This template helps you clearly define which network services are included in your compliance scope, such as your ISP, CDN, DNS, cloud connectivity, and managed security services.

## When to use it

Use this document whenever you need to outline which network services are covered by your ISO 27001 program. Review and update it whenever your network environment changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements in detail.

## 1. Service classes enumerated with assessment depth per class

<<MUST item:A.8.21:scope_classes>>
_Why: 27002:8.21 — network services_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-class criticality tier (drives monitoring intensity + SLA tolerance)

<<MUST item:A.8.21:scope_criticality>>
_Why: Proportionality_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (in-house operated services governed under A.8.20)

<<MUST item:A.8.21:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new service class, new provider, criticality change)

<<SHOULD item:A.8.21:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
