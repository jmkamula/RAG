---
leaf_id: req:A.7.6:work_session_register
control_ref: A.7.6
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Secure Area Work Session Register

> The catalogue of non-routine work sessions in secure areas (maintenance visits, audits, deep-cleans, third-party visits). Each entry: session id, area, purpose, personnel, supervision

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-session unique identifier

<<MUST item:A.7.6:reg_session_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-session secure area

<<MUST item:A.7.6:reg_area>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-session purpose (maintenance / audit / deep-clean / visitor / emergency)

<<MUST item:A.7.6:reg_purpose>>
_Why: 27002:7.6 — authorised_

<<TEXT>>

## 4. Per-session personnel (including third parties, escorts, supervisors)

<<MUST item:A.7.6:reg_personnel>>
_Why: Accountability_

<<TEXT>>

## 5. Per-session entry/exit timestamps

<<MUST item:A.7.6:reg_timestamps>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-session work-permit reference where the permit system applies

<<SHOULD item:A.7.6:reg_work_permit>>
_Why: Cross-leaf coherence_

<<TEXT>>
