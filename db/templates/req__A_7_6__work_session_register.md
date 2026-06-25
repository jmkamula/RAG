---
leaf_id: req:A.7.6:work_session_register
control_ref: A.7.6
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Secure Area Work Session Register

> The catalogue of non-routine work sessions in secure areas (maintenance visits, audits, deep-cleans, third-party visits). Each entry: session id, area, purpose, personnel, supervision

<!-- TABLE-COLUMNS leaf:req:A.7.6:work_session_register -->
<!-- column: item:A.7.6:reg_session_id -->
<!-- column: item:A.7.6:reg_area -->
<!-- column: item:A.7.6:reg_purpose -->
<!-- column: item:A.7.6:reg_personnel -->
<!-- column: item:A.7.6:reg_timestamps -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.6:work_session_register -->
| Reg Session Id | Reg Area | Reg Purpose | Reg Personnel | Reg Timestamps |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.6:work_session_register -->

## Column guidance — what to fill in

### Reg Session Id

<<MUST item:A.7.6:reg_session_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-session unique identifier

### Reg Area

<<MUST item:A.7.6:reg_area>>
_Why: Cross-control coherence_

> _Standard text:_ Per-session secure area

### Reg Purpose

<<MUST item:A.7.6:reg_purpose>>
_Why: 27002:7.6 — authorised_

> _Standard text:_ Per-session purpose (maintenance / audit / deep-clean / visitor / emergency)

### Reg Personnel

<<MUST item:A.7.6:reg_personnel>>
_Why: Accountability_

> _Standard text:_ Per-session personnel (including third parties, escorts, supervisors)

### Reg Timestamps

<<MUST item:A.7.6:reg_timestamps>>
_Why: Operational discipline_

> _Standard text:_ Per-session entry/exit timestamps

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Work Permit

<<SHOULD item:A.7.6:reg_work_permit>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-session work-permit reference where the permit system applies
