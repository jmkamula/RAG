---
leaf_id: req:A.8.34:applicable_audit_testing_scope
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Audit Testing Scope

<<DOC_CONTROL>>

> Upstream — what counts as audit testing on operational systems. Internal audit yes. External pen-test yes. Regulator inspection yes. Routine application testing under A.8.29

## What this template gives you

This template helps you clearly define what types of audit testing are considered relevant for your operational systems, including internal audits, external penetration tests, and regulator inspections.

## When to use it

Use this document whenever you need to clarify or update the scope of audit testing that applies to your environment. Review and refresh it as needed to stay current with your operations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to fill in thoughtfully.

## 1. Engagement types in scope (internal audit / third-party pen-test / regulator inspection / customer security assessment)

<<MUST item:A.8.34:scope_engagement_types>>
_Why: 27002:8.34 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Operational systems in scope (drawn from A.5.9 asset register)

<<MUST item:A.8.34:scope_systems>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (routine application testing via A.8.29; non-operational test-bed work)

<<MUST item:A.8.34:scope_exclusions>>
_Why: Cross-control boundary_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engagement type, new regulator audit power)

<<SHOULD item:A.8.34:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
