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

> Upstream — which engineering domains apply the principles. In-house development typically all yes. Off-the-shelf integration proportional

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Engineering domains enumerated (product / platform / infrastructure / integration / data)

<<MUST item:A.8.27:scope_domains>>
_Why: 27002:8.27 — applied_

<<TEXT>>

## 2. Application depth per domain (full-application for in-house; integration-pattern-only for COTS)

<<MUST item:A.8.27:scope_application>>
_Why: Proportionality_

<<TEXT>>

## 3. Exclusion rationale (e.g. third-party-managed black-box services)

<<MUST item:A.8.27:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engineering paradigm, new threat class)

<<SHOULD item:A.8.27:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
