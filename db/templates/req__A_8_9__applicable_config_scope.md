---
leaf_id: req:A.8.9:applicable_config_scope
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Asset Scope for Configuration Management

> Upstream — which asset classes have baselines, which are vendor-managed (delegated to supplier per A.5.19), which are exception-managed

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset classes enumerated with baseline approach per class

<<MUST item:A.8.9:scope_classes>>
_Why: 27002:8.9 — established_

<<TEXT>>

## 2. Vendor-managed asset classes delegated to A.5.19 supplier obligations

<<MUST item:A.8.9:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded class

<<MUST item:A.8.9:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new vendor, new platform)

<<SHOULD item:A.8.9:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
