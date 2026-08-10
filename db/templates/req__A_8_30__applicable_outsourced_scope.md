---
leaf_id: req:A.8.30:applicable_outsourced_scope
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Outsourced Development Scope

<<DOC_CONTROL>>

> Upstream — what counts as 'outsourced development'. Custom-development contractor yes. Staff augmentation typically governed under A.6.5 + A.5.20. Pre-existing COTS via A.5.19/A.5.20

## What this template gives you

This template helps you clearly define which parts of your development work are considered 'outsourced' for compliance purposes, making it easier to know what needs to be covered under your security program.

## When to use it

Use this document whenever you engage outside contractors for custom software development or when your situation matches the criteria for outsourced development. Update it whenever your outsourcing arrangements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required points and possibly one recommended detail.

## 1. Engagement types in scope (turn-key contract / dedicated team / co-development / pen-test-as-development)

<<MUST item:A.8.30:scope_engagement_types>>
_Why: 27002:8.30 — outsourced_

<<GUIDANCE>>

<<TEXT>>

## 2. Boundary with A.6.5 (staff augmentation governed there) + A.5.20 (general supplier security contract terms)

<<MUST item:A.8.30:scope_boundary_a65>>
_Why: Cross-control boundary_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (e.g. open-source contributions accepted via A.8.4 repo governance)

<<MUST item:A.8.30:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engagement type, new vendor model)

<<SHOULD item:A.8.30:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
