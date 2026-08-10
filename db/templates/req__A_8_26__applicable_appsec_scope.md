---
leaf_id: req:A.8.26:applicable_appsec_scope
control_ref: A.8.26
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Application Security Requirements Scope

<<DOC_CONTROL>>

> Upstream — which applications get full-depth requirements process. Customer-facing typically yes. Internal admin tools proportional. COTS acquired via A.8.30 outsourced governance

## What this template gives you

This template helps you clearly define which of your applications need to follow the full application security requirements, making it easier to prioritize your compliance efforts.

## When to use it

Use this document whenever your application profile matches certain criteria that require a security review, and update it whenever there are changes to your application landscape or compliance needs.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended section.

## 1. Application classes enumerated with depth-of-process per class

<<MUST item:A.8.26:scope_classes>>
_Why: 27002:8.26 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Acquired-applications path (security-requirement check during procurement; cross-link to A.5.19/A.5.20)

<<MUST item:A.8.26:scope_acquired>>
_Why: 27002:8.26 — acquiring applications_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (low-risk internal scripts / experimental prototypes pre-production)

<<MUST item:A.8.26:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new product class, new acquisition pattern, new regulatory regime)

<<SHOULD item:A.8.26:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
