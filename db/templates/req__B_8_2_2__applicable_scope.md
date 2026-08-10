---
leaf_id: req:B.8.2.2:applicable_scope
control_ref: B.8.2.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processing Contexts Scope

<<DOC_CONTROL>>

> The upstream — which processor services fall under B.8.2.2 (customer PII processed on their behalf) as opposed to org's own-controller processing.

## What this template gives you

This template helps you clearly define which processing activities fall under customer data processing versus your own organization's data use, making it easier to demonstrate compliance with privacy requirements.

## When to use it

Use this document whenever your organization processes customer personal data on their behalf, especially when your data handling profile matches relevant privacy triggers. Update it as needed if your processing activities or customer relationships change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and review your processing activities.

## 1. In-scope services enumerated (customer-PII processing services)

<<MUST item:B.8.2.2:scope_services>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Own-controller carve-out — services where org acts as controller (billing / marketing to prospects) excluded with rationale

<<MUST item:B.8.2.2:scope_own_controller>>
_Why: Classification defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Data-flow map — customer PII vs own-controller PII boundary documented

<<MUST item:B.8.2.2:scope_data_flows>>
_Why: §8.2.2 — only processed for purposes_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new service launch / new integration)

<<SHOULD item:B.8.2.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
