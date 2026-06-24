---
leaf_id: req:Art.28:processor_register
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Per-Processor DPA Register

> Per-processor record proving every active processor has a signed DPA in force. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Processor identifier per row (entity name, jurisdiction)

<<MUST item:Art.28:reg_processor_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row data categories processed (cross-link to Art.30 RoPA)

<<MUST item:Art.28:reg_data_categories>>
_Why: Cross-article coherence_

<<TEXT>>

## 3. Per-row DPA version + execution date

<<MUST item:Art.28:reg_dpa_version>>
_Why: Currency_

<<TEXT>>

## 4. Per-row authorised sub-processor list (or 'none')

<<MUST item:Art.28:reg_subprocessors>>
_Why: Art.28.2_

<<TEXT>>

## 5. Per-row Art.32-equivalent security assurance source (certification / audit report / questionnaire)

<<MUST item:Art.28:reg_security_check>>
_Why: Art.28.3c_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row Chap V transfer mechanism where applicable

<<SHOULD item:Art.28:reg_transfer_mechanism>>
_Why: Cross-chapter coherence_

<<TEXT>>
