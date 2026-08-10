---
leaf_id: req:10.1:applicable_triggers_scope
control_ref: 10.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Improvement Triggers Scope

<<DOC_CONTROL>>

> The upstream that bounds the procedure — which signal sources count as improvement triggers vs which route elsewhere (NCs to 10.2; risk-driven changes to 6.1.3; ICT changes to A.8.32)

## What this template gives you

This template helps you clearly define which types of changes or events should be treated as improvement triggers, and which should be managed through other specific processes.

## When to use it

Use this document whenever you need to clarify the boundaries for improvement triggers in your environment, and update it whenever there are changes to your processes or sources of improvement signals.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as each required section will take approximately 10-15 minutes to fill in thoughtfully.

## 1. Internal signal sources in scope (9.1 measurements, 9.2 audit findings non-NC observations, 9.3 mgmt review decisions, 7.3 awareness assessment gaps)

<<MUST item:10.1:scope_internal_signals>>
_Why: Clause 10.1 — triggers_

<<GUIDANCE>>

<<TEXT>>

## 2. External signal sources in scope (4.2 party feedback, regulator updates, sectoral threat intel, surveillance-audit observations)

<<MUST item:10.1:scope_external_signals>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. 10.2 boundary — NCs route to 10.2 NC/CA, NOT to 10.1; observations and opportunities route here

<<MUST item:10.1:scope_10_2_boundary>>
_Why: Cross-clause coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new signal source from new tooling, new feedback channel)

<<SHOULD item:10.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
