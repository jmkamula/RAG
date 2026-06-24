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

> Upstream — which network domains are in scope. Cloud VPCs typically yes. Vendor-managed pass-through ISPs typically delegated. OT typically tighter rules. Multi-tenant systems require per-tenant zones

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Network domains in scope (corporate / cloud / OT / multi-tenant SaaS) with segregation expectation per domain

<<MUST item:A.8.22:scope_domains>>
_Why: 27002:8.22 — appropriate_

<<TEXT>>

## 2. Per-tenant segregation requirements where multi-tenant (data + control + log isolation)

<<MUST item:A.8.22:scope_multi_tenant>>
_Why: 27002:8.22 — appropriate_

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded domain

<<MUST item:A.8.22:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new tenant, new cloud region, new regulator)

<<SHOULD item:A.8.22:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
