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

> Upstream — which applications get full-depth requirements process. Customer-facing typically yes. Internal admin tools proportional. COTS acquired via A.8.30 outsourced governance

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Application classes enumerated with depth-of-process per class

<<MUST item:A.8.26:scope_classes>>
_Why: 27002:8.26 — appropriate_

<<TEXT>>

## 2. Acquired-applications path (security-requirement check during procurement; cross-link to A.5.19/A.5.20)

<<MUST item:A.8.26:scope_acquired>>
_Why: 27002:8.26 — acquiring applications_

<<TEXT>>

## 3. Exclusion rationale (low-risk internal scripts / experimental prototypes pre-production)

<<MUST item:A.8.26:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new product class, new acquisition pattern, new regulatory regime)

<<SHOULD item:A.8.26:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
