---
leaf_id: req:A.7.2:entry_event_register
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Physical Entry Event Register

> The catalogue of entry events into secure areas — badge-swipes, visitor sign-ins, exceptions invoked. Drives 'show me who entered the server room on date X' audit

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-event unique identifier

<<MUST item:A.7.2:reg_event_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-event subject identifier (employee or visitor; for visitors, host also recorded)

<<MUST item:A.7.2:reg_subject>>
_Why: Accountability_

<<TEXT>>

## 3. Per-event area entered (from the perimeter register A.7.1)

<<MUST item:A.7.2:reg_area>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Per-event timestamp (entry; exit timestamp where mantrap enforces it)

<<MUST item:A.7.2:reg_timestamp>>
_Why: 27002:7.2 — controls_

<<TEXT>>

## 5. Per-event entry method (badge / biometric / mechanical / visitor-escort / exception-override)

<<MUST item:A.7.2:reg_method>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Anomaly flag per event (out-of-hours, unusual area for this subject, override-without-justification)

<<SHOULD item:A.7.2:reg_anomaly_flag>>
_Why: Detection_

<<TEXT>>
