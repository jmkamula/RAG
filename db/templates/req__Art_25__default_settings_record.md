---
leaf_id: req:Art.25:default_settings_record
control_ref: Art.25
standard_id: GDPR:2016/679
evidence_type: configuration_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# Privacy-default configuration record (Art.25.2)

> Art.25.2 requires that, by default, only personal data which are necessary for each specific purpose are processed. This is a system property — a record listing the personal-data systems and confirming that their default settings minimise the amount, extent, storage period, and accessibility of personal data. ISO 27001 does not require this as a discrete artifact; Art.25.2 does.

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Personal-data systems inventoried (links to Art.30 records)

<<MUST item:Art.25:default_systems_inventoried>>
_Why: Art.25.2 — scope of obligation_

<<TEXT>>

## 2. Default collection minimises the amount of personal data per purpose

<<MUST item:Art.25:default_amount>>
_Why: Art.25.2 — amount of personal data collected_

<<TEXT>>

## 3. Default processing minimises the extent of processing per purpose

<<MUST item:Art.25:default_extent>>
_Why: Art.25.2 — extent of their processing_

<<TEXT>>

## 4. Default storage period set to the minimum necessary per purpose

<<MUST item:Art.25:default_storage>>
_Why: Art.25.2 — period of their storage_

<<TEXT>>

## 5. Default accessibility limited — data not made accessible to indefinite recipients without intervention

<<MUST item:Art.25:default_accessibility>>
_Why: Art.25.2 — accessibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception register for higher-than-default settings with documented justification

<<SHOULD item:Art.25:default_exception_register>>
_Why: Demonstrates accountability_

<<TEXT>>

### 2. Reference to DPIA process for changes to defaults that increase risk

<<SHOULD item:Art.25:default_review_dpia_link>>
_Why: Art.35 linkage_

<<TEXT>>
