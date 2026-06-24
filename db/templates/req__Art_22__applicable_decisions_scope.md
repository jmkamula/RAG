---
leaf_id: req:Art.22:applicable_decisions_scope
control_ref: Art.22
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Automated Decisions Scope

> The upstream — which automated processes count as 'solely automated' + 'legal effects or similarly significant'. Crucial: routine fraud-detection that flags-for-human-review is OUT of scope; loan-approval decided-by-algorithm is IN scope

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Operational test for 'solely automated' (no meaningful human involvement)

<<MUST item:Art.22:scope_solely_automated>>
_Why: Art.22.1 — solely automated_

<<TEXT>>

## 2. Test for legal or similarly significant effects (financial, employment, insurance, eligibility)

<<MUST item:Art.22:scope_significant_effects>>
_Why: Art.22.1 — significantly affects_

<<TEXT>>

## 3. In-scope systems enumerated

<<MUST item:Art.22:scope_in_scope_systems>>
_Why: Coverage_

<<TEXT>>

## 4. Out-of-scope automated processes (with rationale — e.g. flag-for-review, recommender-no-significant-effect)

<<MUST item:Art.22:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new ML model deployed, system promotion from review to decision)

<<SHOULD item:Art.22:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
