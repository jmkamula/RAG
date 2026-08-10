---
leaf_id: req:Art.30:data_flow_inventory
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: data_flow_inventory
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
table_shape: true
---

# Personal Data Flow Inventory

<<DOC_CONTROL>>

> The upstream data picture that feeds RoPA accuracy. Where the register is activity-centric (one row per processing activity), the data flow inventory is data-centric — which systems hold personal data, how data moves between them, who receives it, and which transfers cross borders. EDPB guidance treats data mapping as the foundation for accurate Art.30 records

<!-- TABLE-COLUMNS leaf:req:Art.30:data_flow_inventory -->
<!-- column: item:Art.30:dfi_systems -->
<!-- column: item:Art.30:dfi_flows -->
<!-- column: item:Art.30:dfi_recipients -->
<!-- column: item:Art.30:dfi_transfers -->
<!-- column: item:Art.30:dfi_retention -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you map out where personal data is stored, how it moves between your systems, and who has access to it, supporting accurate and up-to-date GDPR records.

## When to use it

Use this whenever you need to document your personal data flows, especially if you process personal data in your environment. Update it whenever your data systems or flows change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1–1.5 hours to complete the required sections for a simple environment. More complex organizations with many systems or data flows may need additional time.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.30:data_flow_inventory -->
| Dfi Systems | Dfi Flows | Dfi Recipients | Dfi Transfers | Dfi Retention |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.30:data_flow_inventory -->

## Column guidance — what to fill in

### Dfi Systems

<<MUST item:Art.30:dfi_systems>>
_Why: Art.30.1.c-d foundation_

> _Standard text:_ Systems holding personal data enumerated (production systems, SaaS, backups, analytics, archives)

<<GUIDANCE>>

### Dfi Flows

<<MUST item:Art.30:dfi_flows>>
_Why: Art.30.1.d foundation_

> _Standard text:_ Data flows between systems documented (sources, destinations, integration mechanism)

<<GUIDANCE>>

### Dfi Recipients

<<MUST item:Art.30:dfi_recipients>>
_Why: Art.30.1.d_

> _Standard text:_ External recipients identified per flow (processors, joint controllers, third parties) — feeds Art.30.1.d

<<GUIDANCE>>

### Dfi Transfers

<<MUST item:Art.30:dfi_transfers>>
_Why: Art.30.1.e / Chapter V_

> _Standard text:_ Third-country transfers identified per flow with safeguards (SCCs, adequacy, BCRs) — feeds Art.30.1.e

<<GUIDANCE>>

### Dfi Retention

<<MUST item:Art.30:dfi_retention>>
_Why: Art.30.1.f_

> _Standard text:_ Retention period per system or per data category — feeds Art.30.1.f

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Dfi Asset Link

<<SHOULD item:Art.30:dfi_asset_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to the asset/system inventory (ISO 27001 A.5.9) so the two registers stay aligned

<<GUIDANCE>>

### Dfi Minimisation

<<SHOULD item:Art.30:dfi_minimisation>>
_Why: Art.5.1.c linkage_

> _Standard text:_ Notes data minimisation review touchpoints (Art.5.1.c) — flows or fields flagged for reduction

<<GUIDANCE>>

### Dfi Visual

<<SHOULD item:Art.30:dfi_visual>>
_Why: Auditor/reviewer clarity_

> _Standard text:_ Visual representation (data flow diagram) accompanies the tabular inventory

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
