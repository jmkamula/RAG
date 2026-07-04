---
leaf_id: req:B.8.2.3:applicable_scope
control_ref: B.8.2.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Marketing Activities Scope

> The upstream — which processor activities could touch customer PII for marketing/advertising purposes. For most processors, this scope is empty (customer PII strictly siloed from marketing).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Marketing channels enumerated (email marketing / retargeting / in-product prompts / third-party ad platforms)

<<MUST item:B.8.2.3:scope_marketing_channels>>
_Why: Coverage_

<<TEXT>>

## 2. Customer-PII isolation posture (marketing systems use own-controller data only)

<<MUST item:B.8.2.3:scope_pii_isolation>>
_Why: §8.2.3 — default prohibition_

<<TEXT>>

## 3. Documented exceptions (empty for most processors) with rationale

<<MUST item:B.8.2.3:scope_exceptions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new marketing programme launched / new customer permit request)

<<SHOULD item:B.8.2.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
