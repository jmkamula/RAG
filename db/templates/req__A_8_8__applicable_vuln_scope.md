---
leaf_id: req:A.8.8:applicable_vuln_scope
control_ref: A.8.8
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Asset Scope for Vulnerability Management

<<DOC_CONTROL>>

> Upstream — which asset classes get which scanning approach. Network scan vs agent scan vs SCA vs container image scan vs cloud config scan. Cross-link to A.5.9 register

## What this template gives you

This template helps you clearly define which types of assets in your environment require different vulnerability scanning methods, making it easier to manage and track your security coverage.

## When to use it

Use this document whenever you need to outline or update which assets are included in your vulnerability management program. Review and refresh it as your environment or asset inventory changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on the number of asset types and scanning methods you need to describe.

## 1. Asset classes enumerated with scanning approach per class

<<MUST item:A.8.8:scope_asset_classes>>
_Why: 27002:8.8 — exposure evaluated_

<<GUIDANCE>>

<<TEXT>>

## 2. Target coverage percentage per class (with rationale for gaps)

<<MUST item:A.8.8:scope_coverage_pct>>
_Why: 27002:8.8 — exposure_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (vendor-managed assets covered via supplier obligations A.5.20)

<<MUST item:A.8.8:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new scan tooling, new regulator requirement)

<<SHOULD item:A.8.8:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
