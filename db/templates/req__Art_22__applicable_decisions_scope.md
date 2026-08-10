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

<<DOC_CONTROL>>

> The upstream — which automated processes count as 'solely automated' + 'legal effects or similarly significant'. Crucial: routine fraud-detection that flags-for-human-review is OUT of scope; loan-approval decided-by-algorithm is IN scope

## What this template gives you

This template helps you clearly define which automated decisions in your organization fall under GDPR Article 22, focusing on those with legal or similarly significant effects.

## When to use it

Use this document when your activities involve automated decision-making that could impact individuals in a legally significant way, and update it whenever your processes or triggers change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section will take roughly 10 to 15 minutes to draft.

## 1. Operational test for 'solely automated' (no meaningful human involvement)

<<MUST item:Art.22:scope_solely_automated>>
_Why: Art.22.1 — solely automated_

<<GUIDANCE>>

<<TEXT>>

## 2. Test for legal or similarly significant effects (financial, employment, insurance, eligibility)

<<MUST item:Art.22:scope_significant_effects>>
_Why: Art.22.1 — significantly affects_

<<GUIDANCE>>

<<TEXT>>

## 3. In-scope systems enumerated

<<MUST item:Art.22:scope_in_scope_systems>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 4. Out-of-scope automated processes (with rationale — e.g. flag-for-review, recommender-no-significant-effect)

<<MUST item:Art.22:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new ML model deployed, system promotion from review to decision)

<<SHOULD item:Art.22:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
