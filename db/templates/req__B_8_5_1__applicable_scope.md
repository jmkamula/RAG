---
leaf_id: req:B.8.5.1:applicable_scope
control_ref: B.8.5.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Transfer Scope

<<DOC_CONTROL>>

> The upstream — every cross-jurisdiction customer PII flow (direct + via subprocessors + via support access from other regions).

## What this template gives you

This template helps you clearly define and document the scope of personal data transfers involving processors, including direct transfers, subprocessors, and support access across different regions.

## When to use it

Use this document whenever your organization handles personal data that crosses regional or jurisdictional boundaries, especially if your operations or customer base trigger specific privacy requirements. Update it whenever there are changes to your data flows or processor relationships.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as you'll need to provide details for each required element.

## 1. Direct customer-PII transfers (multi-region cloud / backup + DR)

<<MUST item:B.8.5.1:scope_direct_transfers>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Subprocessor-driven transfers (data flowing to subprocessor regions)

<<MUST item:B.8.5.1:scope_subprocessor_transfers>>
_Why: §8.5.1 — suppliers_

<<GUIDANCE>>

<<TEXT>>

## 3. Support-access transfers (support engineers in different regions accessing customer PII)

<<MUST item:B.8.5.1:scope_support_access>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new subprocessor)

<<SHOULD item:B.8.5.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
