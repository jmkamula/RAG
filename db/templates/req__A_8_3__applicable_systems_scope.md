---
leaf_id: req:A.8.3:applicable_systems_scope
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Systems Scope

> Upstream that drives the register and procedure. Documents which systems fall under A.8.3 governance and how classification tiers map to enforcement strictness

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems enumerated (drawn from A.5.9 asset register, filtered to access-relevant assets)

<<MUST item:A.8.3:scope_systems>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Classification tier → enforcement strictness mapping (public / internal / confidential / restricted → ACL vs RBAC vs MFA-gated)

<<MUST item:A.8.3:scope_tier_map>>
_Why: 27002:8.3 — appropriate_

<<TEXT>>

## 3. Exclusions stated (vendor-managed systems delegated via A.5.19; public-content systems with no restriction)

<<MUST item:A.8.3:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, classification re-tier, regulatory inspection)

<<SHOULD item:A.8.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
