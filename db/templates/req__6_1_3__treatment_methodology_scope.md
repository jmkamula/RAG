---
leaf_id: req:6.1.3:treatment_methodology_scope
control_ref: 6.1.3
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Risk Treatment Methodology Scope

> The upstream that bounds the treatment plan — what options are available (4 standard: modify/share/avoid/retain), residual-acceptance authority, treatment cost-vs-benefit threshold rules

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Treatment options catalog (modify / share / avoid / retain — ISO 31000 4-option model)

<<MUST item:6.1.3:scope_options_catalog>>
_Why: Clause 6.1.3a_

<<TEXT>>

## 2. Residual-risk acceptance authority per band (who can sign off on residual high vs medium vs low)

<<MUST item:6.1.3:scope_acceptance_authority>>
_Why: Clause 6.1.3f_

<<TEXT>>

## 3. Cost-benefit rules for treatment selection (when to mitigate vs accept)

<<MUST item:6.1.3:scope_cost_benefit>>
_Why: Defensible selection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-evaluating treatment (new risk, new control, regulator change)

<<SHOULD item:6.1.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
