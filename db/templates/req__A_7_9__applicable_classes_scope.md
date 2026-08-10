---
leaf_id: req:A.7.9:applicable_classes_scope
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Asset Classes and Destinations Scope

<<DOC_CONTROL>>

> The upstream — which asset classes are in scope and what destinations / scenarios drive special handling

## What this template gives you

This template helps you clearly define which asset classes are included in your compliance scope and highlights any destinations or scenarios that require special handling.

## When to use it

Use this document whenever you need to outline or update the scope of asset classes and destinations relevant to your environment. Review and refresh it as your environment or requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Asset classes covered (laptops, phones, tablets, removable media, recording equipment, key safes in transit)

<<MUST item:A.7.9:scope_asset_classes>>
_Why: 27002:7.9 — relevant assets_

<<GUIDANCE>>

<<TEXT>>

## 2. Destinations / scenarios (home / customer site / conferences / travel — each has risk profile)

<<MUST item:A.7.9:scope_destinations>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

## 3. High-risk-jurisdiction list (extra precautions — loaner-only, data minimisation)

<<MUST item:A.7.9:scope_high_risk_jurisdictions>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new travel-risk geography)

<<SHOULD item:A.7.9:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
