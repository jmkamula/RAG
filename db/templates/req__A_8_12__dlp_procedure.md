---
leaf_id: req:A.8.12:dlp_procedure
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# DLP Operations Procedure

> Operational counterpart — alert triage, false-positive tuning, exception handling, user-education feedback loop

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Alert triage flow (severity → first-responder → outcome)

<<MUST item:A.8.12:proc_triage>>
_Why: 27002:8.12 — measures applied_

<<TEXT>>

## 2. False-positive tuning process (suppression with justification, periodic re-evaluation)

<<MUST item:A.8.12:proc_tuning>>
_Why: Operational sustainability_

<<TEXT>>

## 3. Incident-response integration when leakage confirmed (cross-link to A.5.25 triage + A.5.26 register)

<<MUST item:A.8.12:proc_incident_link>>
_Why: 27002:8.12 — measures_

<<TEXT>>

## 4. User-education feedback loop on what triggers DLP (cross-link to A.6.3)

<<MUST item:A.8.12:proc_user_education>>
_Why: Reduces friction_

<<TEXT>>

## 5. Exception process for time-limited business-justified bypass with InfoSec approval

<<MUST item:A.8.12:proc_exception>>
_Why: 27002:8.12 — appropriate_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (DLP lead with Data Protection partner)

<<SHOULD item:A.8.12:proc_owner>>
_Why: Accountability_

<<TEXT>>
