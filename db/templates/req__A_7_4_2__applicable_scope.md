---
leaf_id: req:A.7.4.2:applicable_scope
control_ref: A.7.4.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processing Operations Scope

<<DOC_CONTROL>>

> The upstream — all internal + integration processing operations that touch PII. Excludes fully-anonymised data operations.

## What this template gives you

This template helps you clearly define which of your internal and integrated processing activities involve personal data, making it easier to demonstrate compliance and manage privacy risks.

## When to use it

Use this document whenever your data processing profile changes in a way that could affect which operations handle personal data, and update it as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements in detail.

## 1. Internal processing operations enumerated (application queries / reports / dashboards / ML pipelines / exports)

<<MUST item:A.7.4.2:scope_internal_operations>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Integration processing (webhooks + third-party enrichment + backup + DR)

<<MUST item:A.7.4.2:scope_integrations>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded operations (anonymised / aggregate) with rationale

<<MUST item:A.7.4.2:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product feature / new analytics pipeline)

<<SHOULD item:A.7.4.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
