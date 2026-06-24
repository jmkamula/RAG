---
leaf_id: req:A.7.13:maintenance_event_register
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Maintenance Event Register

> The catalogue of maintenance events — equipment id, date, provider, supervision, outcome, post-verification

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-event unique identifier

<<MUST item:A.7.13:reg_event_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-event equipment (cross-link to A.5.9 asset register)

<<MUST item:A.7.13:reg_equipment>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-event date

<<MUST item:A.7.13:reg_date>>
_Why: Operational discipline_

<<TEXT>>

## 4. Per-event provider (from authorised list)

<<MUST item:A.7.13:reg_provider>>
_Why: 27002:7.13 — authorised_

<<TEXT>>

## 5. Per-event supervision outcome (in-house supervised / unsupervised-with-justification / pre-cleared provider)

<<MUST item:A.7.13:reg_supervision_outcome>>
_Why: 27002:7.13 — confidentiality_

<<TEXT>>

## 6. Per-event post-verification result (passed / failed-with-action)

<<MUST item:A.7.13:reg_post_verify>>
_Why: 27002:7.13 — integrity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-event offsite-maintenance chain-of-custody where applicable

<<SHOULD item:A.7.13:reg_offsite_chain>>
_Why: Cross-leaf coherence_

<<TEXT>>
