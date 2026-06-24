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

> The upstream that bounds the records — which 6.1.3 plan items are in active 8.3 execution scope, which are deferred or planned for later cycles, which are accepted-as-residual without active treatment

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Active treatment items in scope enumerated (current cycle)

<<MUST item:8.3:scope_active_items>>
_Why: Clause 8.3 — implement_

<<TEXT>>

## 2. Deferred items listed with deferral rationale + next-cycle target

<<MUST item:8.3:scope_deferred_items>>
_Why: Defensibility_

<<TEXT>>

## 3. Accepted-residual items listed (no active treatment but residual signed off per 6.1.3 f))

<<MUST item:8.3:scope_accepted_items>>
_Why: Audit clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new high-risk finding, capacity change, vendor change)

<<SHOULD item:8.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
