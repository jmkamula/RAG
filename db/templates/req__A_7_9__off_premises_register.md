---
leaf_id: req:A.7.9:off_premises_register
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Off-Premises Asset Register

> The catalogue of assets currently off-premises — laptops issued, equipment taken to events, media in transit. Drives 'where is asset X right now' query and loss-detection

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row asset identifier (cross-link to A.5.9 asset register)

<<MUST item:A.7.9:reg_asset_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row current holder (named individual)

<<MUST item:A.7.9:reg_holder>>
_Why: Accountability_

<<TEXT>>

## 3. Per-row off-premises date (drives stale-loaner detection)

<<MUST item:A.7.9:reg_off_since>>
_Why: Operational discipline_

<<TEXT>>

## 4. Per-row expected return date where applicable

<<MUST item:A.7.9:reg_expected_return>>
_Why: 27002:7.9 — registration_

<<TEXT>>

## 5. Per-row status (active-off-premises / returned / lost / stolen / written-off)

<<MUST item:A.7.9:reg_status>>
_Why: Lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row purpose (daily-loaner / conference / customer-visit / permanent-issue)

<<SHOULD item:A.7.9:reg_purpose>>
_Why: Risk profile_

<<TEXT>>
