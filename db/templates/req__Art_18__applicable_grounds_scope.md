---
leaf_id: req:Art.18:applicable_grounds_scope
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Restriction Grounds Scope

> The upstream — operational interpretation of the four Art.18.1 grounds, what the restriction looks like per data class, exception handling per Art.18.2

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Art.18.1 grounds catalog (a-d) with practical examples

<<MUST item:Art.18:scope_grounds_catalog>>
_Why: Art.18.1_

<<TEXT>>

## 2. Data classes covered (each with implementation pattern — flag / partition / lock)

<<MUST item:Art.18:scope_data_classes>>
_Why: Implementation_

<<TEXT>>

## 3. Art.18.2 exceptions enumerated (subject consent / legal claims / protection of rights / important public interest)

<<MUST item:Art.18:scope_art18_2_exceptions>>
_Why: Art.18.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new data class, new system surfacing)

<<SHOULD item:Art.18:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
