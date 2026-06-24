---
leaf_id: req:A.6.8:reporting_audience_scope
control_ref: A.6.8
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Reporting Audience Scope

> The upstream that drives the procedure's audience and the awareness-promotion focus. Documents who CAN report (every person with access — including non-employees), who SHOULD know about the channel, and how the channel surfaces to each segment

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Audience segments enumerated (employees, contractors, suppliers' staff with access, visitors, customers in some sectors — anyone who might observe an event)

<<MUST item:A.6.8:scope_audience_segments>>
_Why: 27002:6.8 — relevant audiences_

<<TEXT>>

## 2. Channel-surfacing per segment (employees see it in onboarding training + intranet; contractors see it at onboarding briefing; visitors see it in lobby; customers in T&Cs)

<<MUST item:A.6.8:scope_channel_surfacing>>
_Why: 27002:6.8 — accessibility_

<<TEXT>>

## 3. Sensitive-case escalation paths stated (insider-threat suspicion → InfoSec-only intake bypassing line management; whistleblower-territory → independent intake)

<<MUST item:A.6.8:scope_sensitive_paths>>
_Why: 27002:6.8 — appropriate channels_

<<TEXT>>

## 4. Jurisdictions covered (whistleblower-protection law variations — EU Whistleblower Directive, US Sarbanes-Oxley, sectoral protections)

<<MUST item:A.6.8:scope_jurisdictions>>
_Why: 27002:6.8 — applicable laws_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new audience segment — e.g. open-source contributors, gig workers, new sectoral whistleblower regulation)

<<SHOULD item:A.6.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
