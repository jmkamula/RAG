---
leaf_id: req:8.2:applicable_assessment_scope
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Operational Assessment Scope

> The upstream that bounds the records — which assets / processes / suppliers are individually assessed at the operational layer (per clause 8.2). Distinct from 6.1.2 (which is the methodology) and 6.1.3 (which is the treatment plan)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset/process classes in scope for operational assessment (production systems, data flows, supplier integrations, deployed products)

<<MUST item:8.2:scope_asset_classes>>
_Why: Clause 8.2 — assess_

<<TEXT>>

## 2. Risk tier per asset class drives cadence (8.2 'planned intervals' is risk-based, not flat)

<<MUST item:8.2:scope_per_class_tier>>
_Why: Defensible cadence_

<<TEXT>>

## 3. Out-of-scope classes (test/dev environments where 6.1.2 already covers them at higher level)

<<MUST item:8.2:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new asset class, sector entry)

<<SHOULD item:8.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
