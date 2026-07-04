---
leaf_id: req:A.7.4.3:applicable_scope
control_ref: A.7.4.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Accuracy Contexts Scope

> The upstream — which PII categories need active accuracy management (contact details + address + payment info + employment status) vs which are relatively static.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. High-churn field categories (contact details / address / employment / preferences)

<<MUST item:A.7.4.3:scope_high_churn_fields>>
_Why: Prioritisation_

<<TEXT>>

## 2. Low-churn field categories (date of birth / national ID / immutable identifiers)

<<MUST item:A.7.4.3:scope_low_churn_fields>>
_Why: Coverage_

<<TEXT>>

## 3. Verification source map (postal address vs national registry vs subject self-serve)

<<MUST item:A.7.4.3:scope_verification_sources>>
_Why: Practicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new PII category / new verification source)

<<SHOULD item:A.7.4.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
