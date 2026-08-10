---
leaf_id: req:A.8.22:applicable_segregation_scope
control_ref: A.8.22
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Segregation Scope

<<DOC_CONTROL>>

> Upstream — which network domains are in scope. Cloud VPCs typically yes. Vendor-managed pass-through ISPs typically delegated. OT typically tighter rules. Multi-tenant systems require per-tenant zones

## What this template gives you

This template helps you clearly define which parts of your network are included in your security program, such as cloud environments, vendor-managed connections, and operational technology zones.

## When to use it

Use this document whenever you need to outline or update the boundaries of your network security scope. It should always reflect your current environment and be refreshed whenever changes occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required areas and possibly one recommended detail.

## 1. Network domains in scope (corporate / cloud / OT / multi-tenant SaaS) with segregation expectation per domain

<<MUST item:A.8.22:scope_domains>>
_Why: 27002:8.22 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-tenant segregation requirements where multi-tenant (data + control + log isolation)

<<MUST item:A.8.22:scope_multi_tenant>>
_Why: 27002:8.22 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded domain

<<MUST item:A.8.22:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new tenant, new cloud region, new regulator)

<<SHOULD item:A.8.22:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
