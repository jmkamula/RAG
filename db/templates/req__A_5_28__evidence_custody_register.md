---
leaf_id: req:A.5.28:evidence_custody_register
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Evidence Custody Register

<<DOC_CONTROL>>

> A.5.28 requires that the integrity and provenance of every evidence package be demonstrable on demand. The custody register catalogues every evidence package handled: id, source incident, evidence type, acquisition method, acquisition hash, current custodian, current location, retention end-date, status (active/handed-over/disposed). It is the operational record that proves chain of custody at audit time

<!-- TABLE-COLUMNS leaf:req:A.5.28:evidence_custody_register -->
<!-- column: item:A.5.28:reg_package_id -->
<!-- column: item:A.5.28:reg_source_incident -->
<!-- column: item:A.5.28:reg_evidence_type -->
<!-- column: item:A.5.28:reg_acquisition_hash -->
<!-- column: item:A.5.28:reg_custodian -->
<!-- column: item:A.5.28:reg_location -->
<!-- column: item:A.5.28:reg_status -->
<!-- column: item:A.5.28:reg_retention_end -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear and auditable record of all evidence packages, showing who handled them, where they are, and their current status. It supports proving the integrity and history of your evidence during audits.

## When to use it

Use this register whenever you handle evidence in your environment, updating it as needed whenever evidence is acquired, transferred, or its status changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch takes about 1.5 to 2 hours for the initial structure and first entry, with each additional evidence package taking 10-15 minutes to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.28:evidence_custody_register -->
| Reg Package Id | Reg Source Incident | Reg Evidence Type | Reg Acquisition Hash | Reg Custodian | Reg Location | Reg Status | Reg Retention End |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.28:evidence_custody_register -->

## Column guidance — what to fill in

### Reg Package Id

<<MUST item:A.5.28:reg_package_id>>
_Why: 27002:5.28 — identification + traceability_

> _Standard text:_ Each evidence package captured with a unique identifier

<<GUIDANCE>>

### Reg Source Incident

<<MUST item:A.5.28:reg_source_incident>>
_Why: Closes loop with [[A.5.26]]_

> _Standard text:_ Source incident reference per row (links to A.5.26 incident register)

<<GUIDANCE>>

### Reg Evidence Type

<<MUST item:A.5.28:reg_evidence_type>>
_Why: 27002:5.28 — categorisation_

> _Standard text:_ Evidence type per row (log export / disk image / memory capture / physical media / statement / photograph)

<<GUIDANCE>>

### Reg Acquisition Hash

<<MUST item:A.5.28:reg_acquisition_hash>>
_Why: 27002:5.28 — integrity_

> _Standard text:_ Acquisition hash per row (cryptographic fingerprint recorded at point of collection)

<<GUIDANCE>>

### Reg Custodian

<<MUST item:A.5.28:reg_custodian>>
_Why: 27002:5.28 — preservation_

> _Standard text:_ Current custodian per row (named individual or sealed-storage location)

<<GUIDANCE>>

### Reg Location

<<MUST item:A.5.28:reg_location>>
_Why: 27002:5.28 — storage_

> _Standard text:_ Current location per row (vault id / cloud bucket reference / external-party receipt id)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.5.28:reg_status>>
_Why: Operational discipline_

> _Standard text:_ Status per row (active / handed-over / disposed) with date of last transition

<<GUIDANCE>>

### Reg Retention End

<<MUST item:A.5.28:reg_retention_end>>
_Why: 27002:5.28 — preservation lifecycle_

> _Standard text:_ Retention end-date per row (drives the disposal_record trigger)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Handover Log

<<SHOULD item:A.5.28:reg_handover_log>>
_Why: Forensic best practice_

> _Standard text:_ Per-handover signature trail (immutable append-only — every transfer logs both releasing and receiving custodian)

<<GUIDANCE>>

### Reg Jurisdiction

<<SHOULD item:A.5.28:reg_jurisdiction>>
_Why: Multi-jurisdiction handling_

> _Standard text:_ Jurisdiction tag per row where evidence may cross borders (drives admissibility considerations)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
