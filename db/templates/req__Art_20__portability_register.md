---
leaf_id: req:Art.20:portability_register
control_ref: Art.20
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Portability Request Register

> Per-request record of Art.20 fulfilments. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row request id (Art.12 register cross-reference)

<<MUST item:Art.20:reg_request_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row applicability decision (in-scope / out-of-scope with grounds)

<<MUST item:Art.20:reg_applicability_decision>>
_Why: Art.20.1_

<<TEXT>>

## 3. Per-row delivered format

<<MUST item:Art.20:reg_format_delivered>>
_Why: Art.20.1_

<<TEXT>>

## 4. Per-row destination (export to subject / direct controller transmission)

<<MUST item:Art.20:reg_destination>>
_Why: Art.20.2_

<<TEXT>>

## 5. Per-row delivery date (within Art.12.3 SLA)

<<MUST item:Art.20:reg_delivery_date>>
_Why: Art.12.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row data volume metric (records / bytes)

<<SHOULD item:Art.20:reg_data_volume>>
_Why: Operational_

<<TEXT>>
