---
leaf_id: req:8.2:applicable_assessment_scope
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Operational Assessment Scope

<<DOC_CONTROL>>

> The upstream that bounds the records — which assets / processes / suppliers are individually assessed at the operational layer (per clause 8.2). Distinct from 6.1.2 (which is the methodology) and 6.1.3 (which is the treatment plan)

## What this template gives you

This template helps you clearly define which assets, processes, or suppliers are included in your operational security assessments, making it easier to understand the boundaries of your compliance activities.

## When to use it

Use this document whenever you need to specify or update the scope of your operational assessments, especially when your environment changes or as part of regular compliance reviews.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements in detail.

## 1. Asset/process classes in scope for operational assessment (production systems, data flows, supplier integrations, deployed products)

<<MUST item:8.2:scope_asset_classes>>
_Why: Clause 8.2 — assess_

<<GUIDANCE>>

<<TEXT>>

## 2. Risk tier per asset class drives cadence (8.2 'planned intervals' is risk-based, not flat)

<<MUST item:8.2:scope_per_class_tier>>
_Why: Defensible cadence_

<<GUIDANCE>>

<<TEXT>>

## 3. Out-of-scope classes (test/dev environments where 6.1.2 already covers them at higher level)

<<MUST item:8.2:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, sector entry)

<<SHOULD item:8.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
