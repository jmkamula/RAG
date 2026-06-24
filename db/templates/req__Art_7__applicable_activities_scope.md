---
leaf_id: req:Art.7:applicable_activities_scope
control_ref: Art.7
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Consent Activities Scope

> The upstream that bounds the register — which processing activities rely on consent (per Art.6.1.a) vs other lawful bases. Without this, consent gets over-applied (worst case: 'consent default') or under-applied (worst case: covert reliance)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Activities using consent as the lawful basis enumerated (drawn from the Art.6 lawful basis register)

<<MUST item:Art.7:scope_consent_activities>>
_Why: Art.6.1.a_

<<TEXT>>

## 2. Rules for when consent overlaps with another basis (Art.7 still applies if consent is the chosen basis even when another basis would also work)

<<MUST item:Art.7:scope_overlap_rules>>
_Why: Defensible bounding_

<<TEXT>>

## 3. Special-category overlay rule — Art.9.2.a explicit consent has stricter capture requirements than Art.6.1.a

<<MUST item:Art.7:scope_special_overlay>>
_Why: Art.9.2.a_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new feature requiring consent, basis change for an existing activity)

<<SHOULD item:Art.7:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
