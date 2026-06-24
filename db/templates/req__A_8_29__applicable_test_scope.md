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

> Upstream — which applications / classes get which test types at which gates. Customer-facing PII-touching = full stack. Internal admin proportional

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Application classes enumerated with test-type matrix per class

<<MUST item:A.8.29:scope_app_classes>>
_Why: 27002:8.29 — appropriate_

<<TEXT>>

## 2. Pen-test scope (which application classes require annual third-party testing)

<<MUST item:A.8.29:scope_pen_test_classes>>
_Why: Independent assurance_

<<TEXT>>

## 3. Exclusion rationale (e.g. throwaway prototypes; internal-tooling micro-services with low blast radius)

<<MUST item:A.8.29:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new app class, new test technique, new regulator)

<<SHOULD item:A.8.29:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
