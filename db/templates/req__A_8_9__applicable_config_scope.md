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

<<DOC_CONTROL>>

> Upstream — which asset classes have baselines, which are vendor-managed (delegated to supplier per A.5.19), which are exception-managed

## What this template gives you

This template helps you clearly define which types of assets in your environment are covered by configuration management, which are managed by vendors, and which are handled as exceptions.

## When to use it

Use this document whenever you need to outline the scope of assets for configuration management in your environment, and update it whenever there are changes to asset classes or management responsibilities.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and optionally add a recommended detail.

## 1. Asset classes enumerated with baseline approach per class

<<MUST item:A.8.9:scope_classes>>
_Why: 27002:8.9 — established_

<<GUIDANCE>>

<<TEXT>>

## 2. Vendor-managed asset classes delegated to A.5.19 supplier obligations

<<MUST item:A.8.9:scope_vendor_managed>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale + compensating controls per excluded class

<<MUST item:A.8.9:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new vendor, new platform)

<<SHOULD item:A.8.9:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
