---
leaf_id: req:A.8.29:applicable_test_scope
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Security Testing Scope

<<DOC_CONTROL>>

> Upstream — which applications / classes get which test types at which gates. Customer-facing PII-touching = full stack. Internal admin proportional

## What this template gives you

This template helps you clearly define which of your applications need security testing, and what kind of testing is appropriate for each, based on their function and data sensitivity.

## When to use it

Use this document whenever your systems or applications match certain risk profiles, such as handling customer PII or internal admin functions. Update it whenever there are significant changes to your application landscape.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to thoughtfully address each required element.

## 1. Application classes enumerated with test-type matrix per class

<<MUST item:A.8.29:scope_app_classes>>
_Why: 27002:8.29 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Pen-test scope (which application classes require annual third-party testing)

<<MUST item:A.8.29:scope_pen_test_classes>>
_Why: Independent assurance_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (e.g. throwaway prototypes; internal-tooling micro-services with low blast radius)

<<MUST item:A.8.29:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new app class, new test technique, new regulator)

<<SHOULD item:A.8.29:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
