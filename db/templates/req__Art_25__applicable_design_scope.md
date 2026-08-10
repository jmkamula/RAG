---
leaf_id: req:Art.25:applicable_design_scope
control_ref: Art.25
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable DPbD Scope

<<DOC_CONTROL>>

> The upstream — which design activities are in Art.25 scope (new product/system/feature design + significant change to existing). Defines the 'at the time of determining means' moment operationally

## What this template gives you

This template helps you clearly define which of your design activities fall under GDPR Article 25, making it easier to identify when data protection by design requirements apply to your projects.

## When to use it

Use this document whenever you are starting a new product, system, or feature design, or making significant changes to existing ones. Review and update it as needed to keep your scope current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements in detail.

## 1. Design activities in scope (new product, new feature, significant change, new processor onboarding)

<<MUST item:Art.25:scope_design_activities>>
_Why: Art.25.1 — determining means_

<<GUIDANCE>>

<<TEXT>>

## 2. Definition of 'significant change' triggering re-design review

<<MUST item:Art.25:scope_significant_change>>
_Why: Art.25.1 — at the time of processing_

<<GUIDANCE>>

<<TEXT>>

## 3. Out-of-scope changes (bug fixes, performance tuning, internal refactoring without processing change)

<<MUST item:Art.25:scope_exclusions>>
_Why: Defensible bounding_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product line, new processor type, regulatory guidance change)

<<SHOULD item:Art.25:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
