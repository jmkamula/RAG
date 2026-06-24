---
leaf_id: req:A.5.9:asset_inventory
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: asset_register
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 6
should_count: 3
---

# Inventory of Information and Associated Assets

> A.5.9 requires an inventory of information and associated assets — including owners — developed and maintained. The register is the live record. Lifecycle procedure, the discovery/onboarding upstream and reconciliation review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset records exist (information assets, software, hardware, services, cloud resources)

<<MUST item:A.5.9:asset_records>>
_Why: 27002:5.9a_

<<TEXT>>

## 2. Owner named per asset (individual or role accountable for protection and risk decisions)

<<MUST item:A.5.9:owner_per_asset>>
_Why: 27002:5.9d — including owners_

<<TEXT>>

## 3. Classification per asset (links to the A.5.12 classification scheme)

<<MUST item:A.5.9:classification>>
_Why: 27002:5.9c / A.5.12_

<<TEXT>>

## 4. Location or hosting system where the asset resides (data centre, cloud region, endpoint pool)

<<MUST item:A.5.9:location>>
_Why: 27002:5.9b_

<<TEXT>>

## 5. Last-updated date per record (proves the register is actively maintained, not snapshotted)

<<MUST item:A.5.9:last_updated>>
_Why: 27002:5.9 — maintained_

<<TEXT>>

## 6. Asset type tag (information / software / hardware / service / facility) so type-specific controls can be applied

<<MUST item:A.5.9:asset_type>>
_Why: 27002:5.9 — categorisation_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Lifecycle status per asset (active, retired, in-procurement, in-disposal)

<<SHOULD item:A.5.9:lifecycle_status>>
_Why: Operational completeness_

<<TEXT>>

### 2. Dependency or relationship to other assets (supports A.8.x topology and risk mapping)

<<SHOULD item:A.5.9:dependencies>>
_Why: Risk traceability_

<<TEXT>>

### 3. Cross-link to GDPR Art.30 data flow inventory where the asset holds personal data

<<SHOULD item:A.5.9:dfi_link>>
_Why: Cross-control coherence_

<<TEXT>>
