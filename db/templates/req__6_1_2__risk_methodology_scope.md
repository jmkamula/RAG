---
leaf_id: req:6.1.2:risk_methodology_scope
control_ref: 6.1.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Risk Assessment Methodology Scope

> The upstream that bounds the procedure — what scoring scale (3×3 / 5×5 / quantitative), what acceptance bands, which asset/process categories are in scope, exclusions

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scoring scale stated (e.g. 5×5 qualitative, ALE quantitative)

<<MUST item:6.1.2:scope_scoring_scale>>
_Why: Clause 6.1.2a — acceptance criteria_

<<TEXT>>

## 2. Acceptance bands stated (low/medium/high → accept/treat thresholds)

<<MUST item:6.1.2:scope_acceptance_bands>>
_Why: Clause 6.1.2a_

<<TEXT>>

## 3. Asset/process classes in scope enumerated (data, systems, people, suppliers, premises)

<<MUST item:6.1.2:scope_asset_classes>>
_Why: Coverage proof_

<<TEXT>>

## 4. Exclusions stated explicitly with rationale

<<MUST item:6.1.2:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Calibration notes (when scoring was last validated against actual incidents)

<<SHOULD item:6.1.2:scope_calibration>>
_Why: Validity_

<<TEXT>>
