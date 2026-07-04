---
leaf_id: req:A.7.3.3:applicable_scope
control_ref: A.7.3.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Delivery Contexts Scope

> The upstream — which delivery contexts are in scope (web, mobile, in-product, kiosk, paper, phone) and where notice-at-collection applies vs after-the-fact indirect collection.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Delivery channels enumerated with notice-at-collection status per channel

<<MUST item:A.7.3.3:scope_delivery_channels>>
_Why: Coverage_

<<TEXT>>

## 2. Indirect-collection handling — where PII sourced from third party, notice within reasonable time per Art.14.3

<<MUST item:A.7.3.3:scope_indirect_collection>>
_Why: GDPR Art.14.3_

<<TEXT>>

## 3. Excluded contexts with rationale (e.g. B2B-only channels where notice is contract-embedded)

<<MUST item:A.7.3.3:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product surface / new data source)

<<SHOULD item:A.7.3.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
