---
leaf_id: req:A.6.8:event_reporting_procedure
control_ref: A.6.8
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Information Security Event Reporting Procedure

> A.6.8 requires the organisation to provide a mechanism for personnel to report observed or suspected information security events through appropriate channels in a timely manner. The procedure documents the channels, what to report, timeliness expectation, no-blame culture, and handoff to triage. The event report register, reporting-audience scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Multiple reporting channels offered (email, hotline, portal, manager, ticket system) — drives discoverability and accessibility under various conditions including when normal tooling is unavailable

<<MUST item:A.6.8:channels>>
_Why: 27002:6.8 — appropriate channels_

<<TEXT>>

## 2. Procedure addresses all personnel (employees, contractors, third parties with access)

<<MUST item:A.6.8:audience>>
_Why: 27002:6.8 — mechanism for personnel_

<<TEXT>>

## 3. What to report — observed events, suspected events, near-misses (no judgement required at reporting stage; over-reporting is preferred to under-reporting)

<<MUST item:A.6.8:what_to_report>>
_Why: 27002:6.8 — observed or suspected_

<<TEXT>>

## 4. Timeliness expectation (e.g. as soon as practicable, within N hours of awareness; tighter for active-attack indicators)

<<MUST item:A.6.8:timeliness>>
_Why: 27002:6.8 — timely manner_

<<TEXT>>

## 5. No-blame / non-retaliation statement encourages honest reporting (drives reporting culture; under-reporting is the #1 risk for incident programs)

<<MUST item:A.6.8:no_blame>>
_Why: Reporting culture_

<<TEXT>>

## 6. Handoff to triage process (A.5.25 assessment-and-decision) on receipt — drives traceability from report through to closure

<<MUST item:A.6.8:handoff_to_triage>>
_Why: Closes the loop with A.5.25_

<<TEXT>>

## 7. Named owner of the procedure (typically InfoSec on-call with HR + Legal partners for sensitive cases)

<<MUST item:A.6.8:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Anonymous reporting option for sensitive cases (drives reporting of insider-threat suspicions and whistleblower-territory cases)

<<SHOULD item:A.6.8:anonymity_option>>
_Why: Maximises reporting_

<<TEXT>>

### 2. Periodic awareness reminders about the channel (links to A.6.3 training programme; channel discoverability decays without reminder)

<<SHOULD item:A.6.8:awareness_promotion>>
_Why: Channel discoverability_

<<TEXT>>

### 3. Acknowledgment-to-reporter expectation stated (closes the feedback loop — reporters who never hear back stop reporting)

<<SHOULD item:A.6.8:acknowledgment>>
_Why: Reporting culture_

<<TEXT>>
