---
leaf_id: req:A.7.2:applicable_areas_scope
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Secure Areas Scope

<<DOC_CONTROL>>

> The upstream that drives the procedure. Documents which areas require physical entry controls and what classification tier each falls under

## What this template gives you

This template helps you clearly identify which areas in your organization need physical entry controls and what level of protection each area requires. It's useful for understanding and documenting your secure spaces for compliance purposes.

## When to use it

Use this document whenever you need to define or update the list of secure areas in your environment. Review and revise it as needed, especially when your physical spaces or security requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe each secure area and its classification in detail.

## 1. Secure areas enumerated per site (drawn from A.7.1 register)

<<MUST item:A.7.2:scope_areas>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-tier entry controls mapping (which areas need badge-only vs MFA vs escort)

<<MUST item:A.7.2:scope_tier_controls>>
_Why: 27002:7.2 — proportional_

<<GUIDANCE>>

<<TEXT>>

## 3. Visitor-accessible areas defined (vs strictly-staff areas)

<<MUST item:A.7.2:scope_visitor_areas>>
_Why: 27002:7.2 — controls_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new secure area, area classification change, sub-letting)

<<SHOULD item:A.7.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
