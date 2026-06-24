---
leaf_id: req:Art.44:transfer_register
control_ref: Art.44
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# International Transfer Register

> Per-transfer record cataloguing every flow of personal data outside EU/EEA — destination, mechanism, last-assessed date. Drives 'show me every transfer with its safeguard' audit. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row unique transfer identifier

<<MUST item:Art.44:reg_transfer_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row data categories (cross-link to Art.30 RoPA)

<<MUST item:Art.44:reg_data_categories>>
_Why: Cross-article coherence_

<<TEXT>>

## 3. Per-row destination country + recipient entity

<<MUST item:Art.44:reg_destination>>
_Why: Art.44 — third country_

<<TEXT>>

## 4. Per-row Art.45/46/47/49 mechanism cited

<<MUST item:Art.44:reg_mechanism>>
_Why: Art.44-49 framework_

<<TEXT>>

## 5. Per-row last-assessed date (drives staleness)

<<MUST item:Art.44:reg_assessed_date>>
_Why: Currency_

<<TEXT>>

## 6. Per-row owner

<<MUST item:Art.44:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row link to Transfer Impact Assessment where Schrems II analysis applies

<<SHOULD item:Art.44:reg_tia_link>>
_Why: Schrems II_

<<TEXT>>
