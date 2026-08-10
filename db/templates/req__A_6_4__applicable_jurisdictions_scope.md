---
leaf_id: req:A.6.4:applicable_jurisdictions_scope
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Jurisdictions and Worker Categories Scope

<<DOC_CONTROL>>

> The upstream that drives procedure variants. Documents which jurisdictions the procedure operates in (employment-law variations affect what's permissible — required-notice periods, just-cause requirements, statutory remediation steps) and how it extends to non-employee workers (contractors get different process leverage)

## What this template gives you

This template helps you clearly define which regions and types of workers your procedures cover, making it easier to comply with local employment laws and handle different worker categories appropriately.

## When to use it

Use this document whenever you need to outline the jurisdictions and worker types your procedures apply to, and update it whenever there are changes in your operating regions or workforce structure.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as you'll need to address several required elements related to jurisdictions and worker categories.

## 1. Jurisdictions covered (employment-law variants — at-will US states vs just-cause EU vs notice-period UK — drive process step variations)

<<MUST item:A.6.4:scope_jurisdictions>>
_Why: 27002:6.4 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

## 2. Worker categories addressed (employees → full process; contractors → contract-based termination; secondees → escalation to home employer)

<<MUST item:A.6.4:scope_worker_categories>>
_Why: 27002:6.4 — interested parties_

<<GUIDANCE>>

<<TEXT>>

## 3. Regulator-notification triggers per jurisdiction (financial-services FSA notification for serious misconduct, healthcare professional body notification)

<<MUST item:A.6.4:scope_regulator_notify>>
_Why: 27002:6.4 — sectoral_

<<GUIDANCE>>

<<TEXT>>

## 4. Legal review path stated (when local employment counsel must be engaged before action — typically all dismissal cases + suspension cases over X days)

<<MUST item:A.6.4:scope_legal_review>>
_Why: 27002:6.4 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new geography, new sectoral regulator, major employment-law reform)

<<SHOULD item:A.6.4:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
