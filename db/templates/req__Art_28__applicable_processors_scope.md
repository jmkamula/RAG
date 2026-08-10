---
leaf_id: req:Art.28:applicable_processors_scope
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processors Scope

<<DOC_CONTROL>>

> The upstream — what counts as a 'processor' (vs joint controller per Art.26, vs intra-group transfer). Operational definition + the controller-vs-processor decision tree

## What this template gives you

This template helps you clearly define which third parties qualify as 'processors' under GDPR, distinguishing them from joint controllers or internal transfers, and provides a decision tree for making these determinations.

## When to use it

Use this document whenever you need to clarify the roles of third parties handling personal data, especially when your business activities or relationships change. Update it as needed to stay accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and review your data processing relationships.

## 1. Processor types in scope (cloud / SaaS providers, payroll, marketing platforms, analytics, support ticketing, etc.)

<<MUST item:Art.28:scope_processor_types>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Controller-vs-processor decision criteria (means & purpose test per EDPB guidelines)

<<MUST item:Art.28:scope_controller_vs_processor>>
_Why: Art.4(7-8) boundary_

<<GUIDANCE>>

<<TEXT>>

## 3. Out-of-scope vendors (those processing only their own data, intra-group with no GDPR transfer)

<<MUST item:Art.28:scope_exclusions>>
_Why: Defensible bounding_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new vendor onboarded, vendor service-shape change)

<<SHOULD item:Art.28:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
