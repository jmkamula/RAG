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
table_shape: true
---

# BCR Coverage Register

> Per-entity record of which group entities are bound by the BCRs + which transfers rely on them. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.47:bcr_register -->
<!-- column: item:Art.47:reg_entity_id -->
<!-- column: item:Art.47:reg_jurisdiction -->
<!-- column: item:Art.47:reg_bcr_role -->
<!-- column: item:Art.47:reg_transfers -->
<!-- column: item:Art.47:reg_signed_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.47:bcr_register -->
| Reg Entity Id | Reg Jurisdiction | Reg Bcr Role | Reg Transfers | Reg Signed Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.47:bcr_register -->

## Column guidance — what to fill in

### Reg Entity Id

<<MUST item:Art.47:reg_entity_id>>
_Why: Audit_

> _Standard text:_ Per-row group entity bound by BCRs

### Reg Jurisdiction

<<MUST item:Art.47:reg_jurisdiction>>
_Why: Defining the relationship_

> _Standard text:_ Per-row jurisdiction of entity

### Reg Bcr Role

<<MUST item:Art.47:reg_bcr_role>>
_Why: Art.47.1_

> _Standard text:_ Per-row BCR role (BCR-C controller / BCR-P processor)

### Reg Transfers

<<MUST item:Art.47:reg_transfers>>
_Why: Cross-leaf_

> _Standard text:_ Per-row transfers covered (link to Art.44 register)

### Reg Signed Date

<<MUST item:Art.47:reg_signed_date>>
_Why: Currency_

> _Standard text:_ Per-row binding-commitment signed date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Complaint Route

<<SHOULD item:Art.47:reg_complaint_route>>
_Why: Art.47.2.i_

> _Standard text:_ Per-row complaint-routing target (group privacy team contact)
