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

> Upstream — which asset classes get which scanning approach. Network scan vs agent scan vs SCA vs container image scan vs cloud config scan. Cross-link to A.5.9 register

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset classes enumerated with scanning approach per class

<<MUST item:A.8.8:scope_asset_classes>>
_Why: 27002:8.8 — exposure evaluated_

<<TEXT>>

## 2. Target coverage percentage per class (with rationale for gaps)

<<MUST item:A.8.8:scope_coverage_pct>>
_Why: 27002:8.8 — exposure_

<<TEXT>>

## 3. Exclusion rationale (vendor-managed assets covered via supplier obligations A.5.20)

<<MUST item:A.8.8:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new scan tooling, new regulator requirement)

<<SHOULD item:A.8.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
