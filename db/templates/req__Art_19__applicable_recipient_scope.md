---
leaf_id: req:Art.19:applicable_recipient_scope
control_ref: Art.19
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Recipients Scope

> The upstream — which recipient classes are in scope for Art.19 notification (processors, joint controllers, downstream controllers, public disclosure under Art.17.2)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recipient classes enumerated (processors, joint controllers, third-country recipients, public)

<<MUST item:Art.19:scope_recipient_classes>>
_Why: Art.19_

<<TEXT>>

## 2. Excluded recipient categories with rationale (e.g. recipients who only received aggregate data)

<<MUST item:Art.19:scope_excluded_recipients>>
_Why: Defensibility_

<<TEXT>>

## 3. Art.17.2 public-disclosure overlay (when erased data was made public, additional notification + take-down efforts required)

<<MUST item:Art.19:scope_art17_2_overlay>>
_Why: Art.17.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new processor onboarded, new joint controller relationship)

<<SHOULD item:Art.19:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
