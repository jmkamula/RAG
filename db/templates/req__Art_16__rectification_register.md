---
leaf_id: req:Art.16:rectification_register
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Rectification Request Register

> Per-request record proving every Art.16 request was handled per procedure. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.16:rectification_register -->
<!-- column: item:Art.16:reg_request_id -->
<!-- column: item:Art.16:reg_subject_id -->
<!-- column: item:Art.16:reg_systems_touched -->
<!-- column: item:Art.16:reg_response_date -->
<!-- column: item:Art.16:reg_art19_xref -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.16:rectification_register -->
| Reg Request Id | Reg Subject Id | Reg Systems Touched | Reg Response Date | Reg Art19 Xref |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.16:rectification_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.16:reg_request_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row request id (Art.12 cross-ref)

### Reg Subject Id

<<MUST item:Art.16:reg_subject_id>>
_Why: Audit_

> _Standard text:_ Per-row subject identifier (pseudonymous)

### Reg Systems Touched

<<MUST item:Art.16:reg_systems_touched>>
_Why: Art.16 — across all instances_

> _Standard text:_ Per-row systems where rectification was applied

### Reg Response Date

<<MUST item:Art.16:reg_response_date>>
_Why: Art.12.3_

> _Standard text:_ Per-row response date (Art.12.3 SLA)

### Reg Art19 Xref

<<MUST item:Art.16:reg_art19_xref>>
_Why: Art.19_

> _Standard text:_ Per-row Art.19 notification reference

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Correction Summary

<<SHOULD item:Art.16:reg_correction_summary>>
_Why: Audit clarity_

> _Standard text:_ Per-row summary of correction made
