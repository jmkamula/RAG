---
leaf_id: req:A.8.1:applicable_endpoint_scope
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Endpoint Scope

<<DOC_CONTROL>>

> Upstream that drives the policy and register. Documents which endpoint classes apply, exclusions (kiosks → A.8.18; servers → A.8.9), and the BYOD authorisation model

## What this template gives you

This template helps you clearly define which types of endpoints are covered by your security policies, including any exceptions and how you handle personally owned devices.

## When to use it

Use this document whenever you need to outline or update which endpoint devices are included in your security program. Review and refresh it as your environment or device policies change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on how many endpoint types and exceptions you need to describe.

## 1. Endpoint classes enumerated (laptop / desktop / mobile / tablet / contractor-owned)

<<MUST item:A.8.1:scope_classes>>
_Why: 27002:8.1 — applicable_

<<GUIDANCE>>

<<TEXT>>

## 2. Exclusions stated explicitly (kiosks via A.8.18, servers via A.8.9, lab/test rigs via A.8.31)

<<MUST item:A.8.1:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

## 3. BYOD authorisation model (allowed / not-allowed / conditional with container)

<<MUST item:A.8.1:scope_byod_model>>
_Why: Common ambiguity point_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new device class, new vendor, regulatory inspection rights)

<<SHOULD item:A.8.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
