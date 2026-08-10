---
leaf_id: req:A.8.27:applicable_architecture_scope
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Architecture Principles Scope

<<DOC_CONTROL>>

> Upstream — which engineering domains apply the principles. In-house development typically all yes. Off-the-shelf integration proportional

## What this template gives you

This template helps you clearly define which parts of your engineering work are covered by your organization’s architecture principles, making it easier to show compliance with ISO 27001 requirements.

## When to use it

Use this document whenever your project or team profile matches specific compliance triggers, and update it as needed if your scope or engineering domains change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to provide details for three required elements.

## 1. Engineering domains enumerated (product / platform / infrastructure / integration / data)

<<MUST item:A.8.27:scope_domains>>
_Why: 27002:8.27 — applied_

<<GUIDANCE>>

<<TEXT>>

## 2. Application depth per domain (full-application for in-house; integration-pattern-only for COTS)

<<MUST item:A.8.27:scope_application>>
_Why: Proportionality_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (e.g. third-party-managed black-box services)

<<MUST item:A.8.27:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engineering paradigm, new threat class)

<<SHOULD item:A.8.27:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
