---
leaf_id: req:Art.14:source_register
control_ref: Art.14
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Art.14 Source Register

> Per-source record — every third-party source from which personal data is obtained, with notice-delivery evidence. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Source identifier per row (data broker name, public source URL, affiliate)

<<MUST item:Art.14:reg_source_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Categories obtained per row (matches Art.14.1d notice item)

<<MUST item:Art.14:reg_category>>
_Why: Coverage_

<<TEXT>>

## 3. Lawful basis per row (Art.6 entry id)

<<MUST item:Art.14:reg_lawful_basis>>
_Why: Cross-article coherence_

<<TEXT>>

## 4. Notice delivery method per row (email, in-app on first communication, etc.)

<<MUST item:Art.14:reg_notice_method>>
_Why: Art.14.3_

<<TEXT>>

## 5. Notice deadline met per row (within 1 month / first communication / first disclosure)

<<MUST item:Art.14:reg_notice_deadline>>
_Why: Art.14.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row Art.14.5 exception cited where notice is not provided (proportionate-impossibility / disclosure-by-law / confidentiality)

<<SHOULD item:Art.14:reg_exception>>
_Why: Art.14.5_

<<TEXT>>
