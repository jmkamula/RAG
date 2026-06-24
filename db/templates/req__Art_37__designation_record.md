---
leaf_id: req:Art.37:designation_record
control_ref: Art.37
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# DPO Designation Record

> Per-DPO designation record (most orgs have 1; group designations may have more). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. DPO identity per row

<<MUST item:Art.37:reg_dpo_identity>>
_Why: Authenticity_

<<TEXT>>

## 2. Per-row qualifications evidence (CV / certifications / professional experience)

<<MUST item:Art.37:reg_qualifications_evidence>>
_Why: Art.37.5_

<<TEXT>>

## 3. Per-row designation date

<<MUST item:Art.37:reg_designation_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-row employment type (internal staff / external service contract)

<<MUST item:Art.37:reg_employment_type>>
_Why: Art.37.6_

<<TEXT>>

## 5. Per-row publication evidence (privacy notice URL + SA notification confirmation)

<<MUST item:Art.37:reg_publication_evidence>>
_Why: Art.37.7_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row link to employment / service contract document

<<SHOULD item:Art.37:reg_contract_link>>
_Why: Audit defensibility_

<<TEXT>>
