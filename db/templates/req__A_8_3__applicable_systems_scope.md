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

<<DOC_CONTROL>>

> Upstream that drives the register and procedure. Documents which systems fall under A.8.3 governance and how classification tiers map to enforcement strictness

## What this template gives you

This template helps you clearly identify which systems in your environment are covered by A.8.3 governance and explains how different classification levels affect the rules you need to follow.

## When to use it

Use this document whenever you need to define or update the list of systems under A.8.3, as it should always reflect your current environment and be refreshed whenever changes occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on how many systems you need to review and classify.

## 1. Systems enumerated (drawn from A.5.9 asset register, filtered to access-relevant assets)

<<MUST item:A.8.3:scope_systems>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Classification tier → enforcement strictness mapping (public / internal / confidential / restricted → ACL vs RBAC vs MFA-gated)

<<MUST item:A.8.3:scope_tier_map>>
_Why: 27002:8.3 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusions stated (vendor-managed systems delegated via A.5.19; public-content systems with no restriction)

<<MUST item:A.8.3:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, classification re-tier, regulatory inspection)

<<SHOULD item:A.8.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
