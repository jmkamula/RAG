---
leaf_id: req:8.3:applicable_treatment_plan_scope
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Treatment Plan Scope

<<DOC_CONTROL>>

> The upstream that bounds the records — which 6.1.3 plan items are in active 8.3 execution scope, which are deferred or planned for later cycles, which are accepted-as-residual without active treatment

## What this template gives you

This template helps you clearly outline which treatment plan items are currently being addressed, which are scheduled for future action, and which are acknowledged but not actively managed. It provides a structured way to communicate your treatment plan's current scope.

## When to use it

Use this document whenever you need to define or update the scope of your treatment plan, as it always applies to your environment. Refresh it as needed, especially when your plan's status or priorities change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as each required section takes roughly 10 to 15 minutes to fill out thoughtfully.

## 1. Active treatment items in scope enumerated (current cycle)

<<MUST item:8.3:scope_active_items>>
_Why: Clause 8.3 — implement_

<<GUIDANCE>>

<<TEXT>>

## 2. Deferred items listed with deferral rationale + next-cycle target

<<MUST item:8.3:scope_deferred_items>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Accepted-residual items listed (no active treatment but residual signed off per 6.1.3 f))

<<MUST item:8.3:scope_accepted_items>>
_Why: Audit clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new high-risk finding, capacity change, vendor change)

<<SHOULD item:8.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
