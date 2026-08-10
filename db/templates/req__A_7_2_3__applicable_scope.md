---
leaf_id: req:A.7.2.3:applicable_scope
control_ref: A.7.2.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Consent Contexts Scope

<<DOC_CONTROL>>

> The upstream — which activities require consent (as opposed to relying on other Art.6 bases). Handles special categories where consent is the only viable basis + children where parental consent is required.

## What this template gives you

This template helps you clearly define which of your activities require consent, especially for sensitive data or when dealing with children. It ensures you meet privacy standards by documenting when consent is the only valid legal basis.

## When to use it

Use this template whenever your activities involve processing special categories of data or children's information, and you need to confirm that consent is required. Update it whenever your data processing activities or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this document from scratch, as you’ll need to address three required elements and review your data processing activities.

## 1. Consent-required activity list (marketing / cookies non-essential / research participation / children)

<<MUST item:A.7.2.3:scope_consent_activities>>
_Why: §7.2.3 — when needed_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-jurisdiction age-of-consent thresholds

<<MUST item:A.7.2.3:scope_children_thresholds>>
_Why: GDPR Art.8 — 16 default, MS variation 13-16_

<<GUIDANCE>>

<<TEXT>>

## 3. Special-category consent map — health / biometric / genetic / criminal / children require explicit consent unless another Art.9.2 basis applies

<<MUST item:A.7.2.3:scope_special_category_map>>
_Why: GDPR Art.9.2.a_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new marketing programme, new sensitive data collection)

<<SHOULD item:A.7.2.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
