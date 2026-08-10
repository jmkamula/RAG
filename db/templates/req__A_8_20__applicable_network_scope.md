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

<<DOC_CONTROL>>

> Upstream — which networks are in scope (corporate LAN / WAN / wireless / cloud VPC / partner connection / OT). Exclusions (e.g. cloud-managed networks delegated to A.5.19/A.5.21)

## What this template gives you

This template helps you clearly define which parts of your network are included in your security program, including any exclusions. It ensures everyone understands the boundaries of your network responsibilities.

## When to use it

Use this document whenever you need to describe the scope of your network for compliance or security purposes. Update it whenever there are changes to your network environment or responsibilities.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements and consider any recommended details.

## 1. Network classes enumerated (corporate LAN / WAN / wireless / cloud VPC / partner connect / OT)

<<MUST item:A.8.20:scope_classes>>
_Why: 27002:8.20 — networks_

<<GUIDANCE>>

<<TEXT>>

## 2. Vendor-managed networks delegated to A.5.19/A.5.21 supplier obligations

<<MUST item:A.8.20:scope_vendor_managed>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded class

<<MUST item:A.8.20:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new cloud region, new partner, new OT environment)

<<SHOULD item:A.8.20:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
