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

> Upstream — what counts as 'network service' for A.8.21. ISP / CDN / DNS / SD-WAN / cloud connectivity / managed-firewall / VPN-as-service all in scope

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Service classes enumerated with assessment depth per class

<<MUST item:A.8.21:scope_classes>>
_Why: 27002:8.21 — network services_

<<TEXT>>

## 2. Per-class criticality tier (drives monitoring intensity + SLA tolerance)

<<MUST item:A.8.21:scope_criticality>>
_Why: Proportionality_

<<TEXT>>

## 3. Exclusion rationale (in-house operated services governed under A.8.20)

<<MUST item:A.8.21:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new service class, new provider, criticality change)

<<SHOULD item:A.8.21:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
