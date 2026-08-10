---
leaf_id: req:A.7.5.2:applicable_scope
control_ref: A.7.5.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Destinations Scope

<<DOC_CONTROL>>

> The upstream — every jurisdiction where PII may be processed (direct + via subprocessor + via support access + via M&A). Excludes law-enforcement-request destinations documented separately.

## What this template gives you

This template helps you clearly outline all the countries and regions where personal data might be processed, including by your vendors or during support activities. It ensures you have a complete view of your data’s geographic footprint.

## When to use it

Use this document whenever your organization processes personal data and needs to identify all relevant jurisdictions, especially if your operations or vendor relationships change. Update it whenever there are changes to your data processing locations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to gather and describe information for each required element.

## 1. Normal-operations destinations (direct + subprocessor + support tier)

<<MUST item:A.7.5.2:scope_normal_operations>>
_Why: §7.5.2 — normal operations_

<<GUIDANCE>>

<<TEXT>>

## 2. Law-enforcement-request handling (not in advance-disclosed list)

<<MUST item:A.7.5.2:scope_law_enforcement>>
_Why: §7.5.2 — cannot be specified in advance_

<<GUIDANCE>>

<<TEXT>>

## 3. Multi-region cloud + backup destinations included

<<MUST item:A.7.5.2:scope_multi_region_cloud>>
_Why: Comprehensiveness_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new subprocessor)

<<SHOULD item:A.7.5.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
