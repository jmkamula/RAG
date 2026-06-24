---
leaf_id: req:Art.32:risk_appropriate_measures_register
control_ref: Art.32
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Risk-Appropriate Measures Register (Art.32.1)

> Per-processing register documenting why the implemented T&O measures are 'appropriate' given the risk. Art.32.1 mandates risk-proportionate measures — without an explicit register, the proportionality argument is implicit and weak. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row processing activity (Art.30 RoPA cross-reference)

<<MUST item:Art.32:reg_activity_id>>
_Why: Cross-article coherence_

<<TEXT>>

## 2. Per-row risk-to-rights-and-freedoms assessment (likelihood + severity)

<<MUST item:Art.32:reg_risk_assessment>>
_Why: Art.32.2 — risks for rights_

<<TEXT>>

## 3. Per-row T&O measures applied (pseudonymisation / encryption / CIA / resilience / restoration)

<<MUST item:Art.32:reg_measures>>
_Why: Art.32.1.a-d_

<<TEXT>>

## 4. Per-row appropriateness justification (state of art / cost / nature of processing weighted against risk)

<<MUST item:Art.32:reg_appropriateness>>
_Why: Art.32.1 — appropriate to risk_

<<TEXT>>

## 5. Per-row owner

<<MUST item:Art.32:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row mapping to implementing ISO 27001 controls

<<SHOULD item:Art.32:reg_iso_mapping>>
_Why: Cross-standard traceability_

<<TEXT>>
