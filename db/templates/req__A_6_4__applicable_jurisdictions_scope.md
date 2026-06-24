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

> The upstream that drives procedure variants. Documents which jurisdictions the procedure operates in (employment-law variations affect what's permissible — required-notice periods, just-cause requirements, statutory remediation steps) and how it extends to non-employee workers (contractors get different process leverage)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Jurisdictions covered (employment-law variants — at-will US states vs just-cause EU vs notice-period UK — drive process step variations)

<<MUST item:A.6.4:scope_jurisdictions>>
_Why: 27002:6.4 — applicable laws_

<<TEXT>>

## 2. Worker categories addressed (employees → full process; contractors → contract-based termination; secondees → escalation to home employer)

<<MUST item:A.6.4:scope_worker_categories>>
_Why: 27002:6.4 — interested parties_

<<TEXT>>

## 3. Regulator-notification triggers per jurisdiction (financial-services FSA notification for serious misconduct, healthcare professional body notification)

<<MUST item:A.6.4:scope_regulator_notify>>
_Why: 27002:6.4 — sectoral_

<<TEXT>>

## 4. Legal review path stated (when local employment counsel must be engaged before action — typically all dismissal cases + suspension cases over X days)

<<MUST item:A.6.4:scope_legal_review>>
_Why: 27002:6.4 — applicable laws_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new geography, new sectoral regulator, major employment-law reform)

<<SHOULD item:A.6.4:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
