---
leaf_id: req:Art.9:applicable_categories_scope
control_ref: Art.9
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Special Categories Scope

> The upstream — which Art.9.1 categories the org actually processes, which Art.9.2 conditions are in use, what's out of scope. Categorical clarity prevents 'we don't process special category data' assertions that are technically false (e.g. CVs revealing trade-union membership)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Art.9.1 categories actually processed enumerated

<<MUST item:Art.9:scope_categories_in_use>>
_Why: Art.9.1_

<<TEXT>>

## 2. Art.9.2 conditions in use across activities (a-j)

<<MUST item:Art.9:scope_conditions_in_use>>
_Why: Art.9.2_

<<TEXT>>

## 3. Categories explicitly NOT processed (with rationale — important for audit clarity)

<<MUST item:Art.9:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

## 4. Member State derogations applied (Art.9.4 — Member States may maintain further conditions for genetic / biometric / health data)

<<MUST item:Art.9:scope_member_state_overlay>>
_Why: Art.9.4_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (HR system change capturing new category, new healthcare line)

<<SHOULD item:Art.9:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
