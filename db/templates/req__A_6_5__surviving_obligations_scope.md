---
leaf_id: req:A.6.5:surviving_obligations_scope
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Surviving Obligations Scope

> The upstream that drives which obligations apply to which roles. Documents the obligation catalogue, the role-to-obligation mapping (executive vs senior vs standard get different post-employment terms), and the jurisdictional caps (where law limits enforceability of e.g. non-compete)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Obligation catalogue enumerated (confidentiality / IP / non-disparagement / non-poach / non-compete / cooperation-with-investigations)

<<MUST item:A.6.5:scope_obligation_catalogue>>
_Why: 27002:6.5 — duties enumerated_

<<TEXT>>

## 2. Role-to-obligation mapping (executive level may have extended non-compete; standard staff only confidentiality + IP; sales/CSM commonly have non-poach + non-solicit)

<<MUST item:A.6.5:scope_role_mapping>>
_Why: 27002:6.5 — proportional_

<<TEXT>>

## 3. Jurisdictional limits on enforceability (US California voids non-compete; EU restricts duration; UK courts test reasonableness)

<<MUST item:A.6.5:scope_jurisdictional_limits>>
_Why: 27002:6.5 — applicable laws_

<<TEXT>>

## 4. Worker categories addressed (employees vs contractors vs interns — different obligation scope)

<<MUST item:A.6.5:scope_worker_categories>>
_Why: 27002:6.5 — interested parties_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new geography with distinct employment law, major employment-law reform, sectoral regulator action)

<<SHOULD item:A.6.5:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
