---
leaf_id: req:A.8.16:applicable_monitoring_scope
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Monitoring Scope

> Upstream — which asset classes are in scope, what coverage is expected (full / sampled / boundary-only), which are vendor-managed (delegated A.5.19/A.5.21)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset classes enumerated with monitoring coverage expectation per class

<<MUST item:A.8.16:scope_classes>>
_Why: 27002:8.16 — networks, systems, applications_

<<TEXT>>

## 2. Vendor-managed monitoring delegated to A.5.19/A.5.21 supplier obligations with evidence of effectiveness

<<MUST item:A.8.16:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale + compensating controls

<<MUST item:A.8.16:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, new attack-vector category, regulator inspection)

<<SHOULD item:A.8.16:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
