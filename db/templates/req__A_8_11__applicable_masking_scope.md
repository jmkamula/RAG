---
leaf_id: req:A.8.11:applicable_masking_scope
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Masking Scope

<<DOC_CONTROL>>

> Upstream — which datasets need masking when entering non-production. Drawn from A.5.34 PII inventory + A.5.12 classification. Documents exclusion rationale (e.g. synthetic-only test data)

## What this template gives you

This template helps you clearly identify which datasets need data masking before they are used in non-production environments, and explains why certain datasets may be excluded, such as when only synthetic test data is used.

## When to use it

Use this document whenever you need to define or update which datasets require masking in your environment. Review and refresh it as your data inventory or classification changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Datasets enumerated with masking obligation per dataset (drawn from A.5.34 PII inventory)

<<MUST item:A.8.11:scope_datasets>>
_Why: 27002:8.11 — appropriate use_

<<GUIDANCE>>

<<TEXT>>

## 2. Non-production environment classes enumerated (dev / test / staging / training / demo / sandbox)

<<MUST item:A.8.11:scope_environments>>
_Why: 27002:8.11 — applicable_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale where masking not required (synthetic-only test data; production-only systems with no non-prod)

<<MUST item:A.8.11:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new dataset, new non-prod environment, new PII class)

<<SHOULD item:A.8.11:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
