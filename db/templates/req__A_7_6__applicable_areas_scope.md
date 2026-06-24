---
leaf_id: req:A.7.6:applicable_areas_scope
control_ref: A.7.6
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Secure Areas Scope

> The upstream — which areas are 'secure' for A.7.6 purposes (drawn from A.7.1 classification), and what additional rules apply per tier

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Secure areas in scope (drawn from A.7.1 register)

<<MUST item:A.7.6:scope_areas>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-tier rule variations (server-room rules vs document-vault rules vs lab rules)

<<MUST item:A.7.6:scope_tier_rules>>
_Why: 27002:7.6 — proportional_

<<TEXT>>

## 3. Third-party categories addressed (cleaning, maintenance contractors, regulators on-site, customers)

<<MUST item:A.7.6:scope_third_party_categories>>
_Why: 27002:7.6 — interested parties_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new secure area, new third-party access pattern)

<<SHOULD item:A.7.6:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
