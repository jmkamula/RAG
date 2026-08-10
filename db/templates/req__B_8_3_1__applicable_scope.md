---
leaf_id: req:B.8.3.1:applicable_scope
control_ref: B.8.3.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Support Scope

<<DOC_CONTROL>>

> The upstream — which customer engagements involve PII processing on their behalf (from B.8.2.1) and therefore require subject-rights support paths.

## What this template gives you

This template helps you clearly define which customer engagements involve processing personal data, so you can identify when privacy rights support is needed for your clients.

## When to use it

Use this document whenever you start a new customer engagement that might involve handling personal information, and update it whenever your data processing activities change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements.

## 1. Customer engagements enumerated (link to B.8.2.1 register)

<<MUST item:B.8.3.1:scope_customer_engagements>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Support matrix per contract tier (Enterprise API access / Business self-service / Startup email support)

<<MUST item:B.8.3.1:scope_support_matrix>>
_Why: Consistency_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded engagements (own-controller services) with rationale

<<MUST item:B.8.3.1:scope_exclusions>>
_Why: Classification_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new contract tier / new self-service feature)

<<SHOULD item:B.8.3.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
