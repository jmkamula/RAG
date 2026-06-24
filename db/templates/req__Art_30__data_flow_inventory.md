---
leaf_id: req:Art.30:data_flow_inventory
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: data_flow_inventory
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
---

# Personal Data Flow Inventory

> The upstream data picture that feeds RoPA accuracy. Where the register is activity-centric (one row per processing activity), the data flow inventory is data-centric — which systems hold personal data, how data moves between them, who receives it, and which transfers cross borders. EDPB guidance treats data mapping as the foundation for accurate Art.30 records

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems holding personal data enumerated (production systems, SaaS, backups, analytics, archives)

<<MUST item:Art.30:dfi_systems>>
_Why: Art.30.1.c-d foundation_

<<TEXT>>

## 2. Data flows between systems documented (sources, destinations, integration mechanism)

<<MUST item:Art.30:dfi_flows>>
_Why: Art.30.1.d foundation_

<<TEXT>>

## 3. External recipients identified per flow (processors, joint controllers, third parties) — feeds Art.30.1.d

<<MUST item:Art.30:dfi_recipients>>
_Why: Art.30.1.d_

<<TEXT>>

## 4. Third-country transfers identified per flow with safeguards (SCCs, adequacy, BCRs) — feeds Art.30.1.e

<<MUST item:Art.30:dfi_transfers>>
_Why: Art.30.1.e / Chapter V_

<<TEXT>>

## 5. Retention period per system or per data category — feeds Art.30.1.f

<<MUST item:Art.30:dfi_retention>>
_Why: Art.30.1.f_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to the asset/system inventory (ISO 27001 A.5.9) so the two registers stay aligned

<<SHOULD item:Art.30:dfi_asset_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Notes data minimisation review touchpoints (Art.5.1.c) — flows or fields flagged for reduction

<<SHOULD item:Art.30:dfi_minimisation>>
_Why: Art.5.1.c linkage_

<<TEXT>>

### 3. Visual representation (data flow diagram) accompanies the tabular inventory

<<SHOULD item:Art.30:dfi_visual>>
_Why: Auditor/reviewer clarity_

<<TEXT>>
