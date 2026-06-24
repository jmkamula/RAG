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

> The upstream — which design activities are in Art.25 scope (new product/system/feature design + significant change to existing). Defines the 'at the time of determining means' moment operationally

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Design activities in scope (new product, new feature, significant change, new processor onboarding)

<<MUST item:Art.25:scope_design_activities>>
_Why: Art.25.1 — determining means_

<<TEXT>>

## 2. Definition of 'significant change' triggering re-design review

<<MUST item:Art.25:scope_significant_change>>
_Why: Art.25.1 — at the time of processing_

<<TEXT>>

## 3. Out-of-scope changes (bug fixes, performance tuning, internal refactoring without processing change)

<<MUST item:Art.25:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product line, new processor type, regulatory guidance change)

<<SHOULD item:Art.25:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
