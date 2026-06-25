---
leaf_id: req:A.7.14:disposal_record
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# Per-Equipment Disposal Record

> Lifecycle-end variant — one record per piece of equipment disposed of. Proves the chain-of-custody from collection through to destruction-or-handover. Parallel to A.5.28 evidence-disposal pattern

<!-- TABLE-COLUMNS leaf:req:A.7.14:disposal_record -->
<!-- column: item:A.7.14:disp_equipment_id -->
<!-- column: item:A.7.14:disp_trigger -->
<!-- column: item:A.7.14:disp_method -->
<!-- column: item:A.7.14:disp_authoriser -->
<!-- column: item:A.7.14:disp_destination -->
<!-- column: item:A.7.14:disp_certificate -->
<!-- column: item:A.7.14:disp_software_step -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.14:disposal_record -->
| Disp Equipment Id | Disp Trigger | Disp Method | Disp Authoriser | Disp Destination | Disp Certificate | Disp Software Step |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.14:disposal_record -->

## Column guidance — what to fill in

### Disp Equipment Id

<<MUST item:A.7.14:disp_equipment_id>>
_Why: 27002:7.14 — traceability_

> _Standard text:_ Per-record equipment identifier (cross-link to A.5.9 asset register, retired entry)

### Disp Trigger

<<MUST item:A.7.14:disp_trigger>>
_Why: 27002:7.14 — disposal_

> _Standard text:_ Per-record disposal trigger

### Disp Method

<<MUST item:A.7.14:disp_method>>
_Why: 27002:7.14 — secure removal_

> _Standard text:_ Per-record method actually used (overwrite tool + verification, degauss, physical destruction with witness)

### Disp Authoriser

<<MUST item:A.7.14:disp_authoriser>>
_Why: Accountability_

> _Standard text:_ Per-record authoriser

### Disp Destination

<<MUST item:A.7.14:disp_destination>>
_Why: 27002:7.14 — securely_

> _Standard text:_ Per-record destination (which approved provider OR internal-witness destruction)

### Disp Certificate

<<MUST item:A.7.14:disp_certificate>>
_Why: Auditability_

> _Standard text:_ Per-record certificate of destruction (where externally destroyed) or witness signature (where internally destroyed)

### Disp Software Step

<<MUST item:A.7.14:disp_software_step>>
_Why: 27002:7.14 — licensed software_

> _Standard text:_ Per-record software-removal step evidence (license-key handoff or wipe)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Disp Re Use Status

<<SHOULD item:A.7.14:disp_re_use_status>>
_Why: Re-use case_

> _Standard text:_ Per-record re-use status where the equipment goes to internal re-use (new owner + re-provisioned configuration link)
