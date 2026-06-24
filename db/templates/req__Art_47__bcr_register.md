---
leaf_id: req:Art.47:bcr_register
control_ref: Art.47
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# BCR Coverage Register

> Per-entity record of which group entities are bound by the BCRs + which transfers rely on them. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row group entity bound by BCRs

<<MUST item:Art.47:reg_entity_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row jurisdiction of entity

<<MUST item:Art.47:reg_jurisdiction>>
_Why: Defining the relationship_

<<TEXT>>

## 3. Per-row BCR role (BCR-C controller / BCR-P processor)

<<MUST item:Art.47:reg_bcr_role>>
_Why: Art.47.1_

<<TEXT>>

## 4. Per-row transfers covered (link to Art.44 register)

<<MUST item:Art.47:reg_transfers>>
_Why: Cross-leaf_

<<TEXT>>

## 5. Per-row binding-commitment signed date

<<MUST item:Art.47:reg_signed_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row complaint-routing target (group privacy team contact)

<<SHOULD item:Art.47:reg_complaint_route>>
_Why: Art.47.2.i_

<<TEXT>>
