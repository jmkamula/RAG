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

<<DOC_CONTROL>>

> The upstream that drives which obligations apply to which roles. Documents the obligation catalogue, the role-to-obligation mapping (executive vs senior vs standard get different post-employment terms), and the jurisdictional caps (where law limits enforceability of e.g. non-compete)

## What this template gives you

This template helps you clearly outline which post-employment obligations apply to different roles in your organization, including any legal limits based on location. It ensures everyone understands their responsibilities and the rules that apply.

## When to use it

Use this document whenever you need to define or update which obligations apply to various roles, especially when roles or legal requirements change. Review and refresh it as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this template from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Obligation catalogue enumerated (confidentiality / IP / non-disparagement / non-poach / non-compete / cooperation-with-investigations)

<<MUST item:A.6.5:scope_obligation_catalogue>>
_Why: 27002:6.5 — duties enumerated_

<<GUIDANCE>>

<<TEXT>>

## 2. Role-to-obligation mapping (executive level may have extended non-compete; standard staff only confidentiality + IP; sales/CSM commonly have non-poach + non-solicit)

<<MUST item:A.6.5:scope_role_mapping>>
_Why: 27002:6.5 — proportional_

<<GUIDANCE>>

<<TEXT>>

## 3. Jurisdictional limits on enforceability (US California voids non-compete; EU restricts duration; UK courts test reasonableness)

<<MUST item:A.6.5:scope_jurisdictional_limits>>
_Why: 27002:6.5 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

## 4. Worker categories addressed (employees vs contractors vs interns — different obligation scope)

<<MUST item:A.6.5:scope_worker_categories>>
_Why: 27002:6.5 — interested parties_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new geography with distinct employment law, major employment-law reform, sectoral regulator action)

<<SHOULD item:A.6.5:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
