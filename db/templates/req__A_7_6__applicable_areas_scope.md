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

<<DOC_CONTROL>>

> The upstream — which areas are 'secure' for A.7.6 purposes (drawn from A.7.1 classification), and what additional rules apply per tier

## What this template gives you

This template helps you clearly define which areas in your environment are considered 'secure' and what extra rules apply to them, making it easier to meet ISO 27001 requirements.

## When to use it

Use this document whenever you need to clarify or update which parts of your environment are classified as secure, and revisit it whenever there are changes to your environment or security requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes drafting this from scratch, as you'll need to identify secure areas and describe the rules that apply to each.

## 1. Secure areas in scope (drawn from A.7.1 register)

<<MUST item:A.7.6:scope_areas>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-tier rule variations (server-room rules vs document-vault rules vs lab rules)

<<MUST item:A.7.6:scope_tier_rules>>
_Why: 27002:7.6 — proportional_

<<GUIDANCE>>

<<TEXT>>

## 3. Third-party categories addressed (cleaning, maintenance contractors, regulators on-site, customers)

<<MUST item:A.7.6:scope_third_party_categories>>
_Why: 27002:7.6 — interested parties_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new secure area, new third-party access pattern)

<<SHOULD item:A.7.6:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
