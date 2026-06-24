---
leaf_id: req:A.8.20:applicable_network_scope
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Network Scope

> Upstream — which networks are in scope (corporate LAN / WAN / wireless / cloud VPC / partner connection / OT). Exclusions (e.g. cloud-managed networks delegated to A.5.19/A.5.21)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Network classes enumerated (corporate LAN / WAN / wireless / cloud VPC / partner connect / OT)

<<MUST item:A.8.20:scope_classes>>
_Why: 27002:8.20 — networks_

<<TEXT>>

## 2. Vendor-managed networks delegated to A.5.19/A.5.21 supplier obligations

<<MUST item:A.8.20:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded class

<<MUST item:A.8.20:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new cloud region, new partner, new OT environment)

<<SHOULD item:A.8.20:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
