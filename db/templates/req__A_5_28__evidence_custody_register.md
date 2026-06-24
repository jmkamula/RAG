---
leaf_id: req:A.5.28:evidence_custody_register
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# Evidence Custody Register

> A.5.28 requires that the integrity and provenance of every evidence package be demonstrable on demand. The custody register catalogues every evidence package handled: id, source incident, evidence type, acquisition method, acquisition hash, current custodian, current location, retention end-date, status (active/handed-over/disposed). It is the operational record that proves chain of custody at audit time

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each evidence package captured with a unique identifier

<<MUST item:A.5.28:reg_package_id>>
_Why: 27002:5.28 — identification + traceability_

<<TEXT>>

## 2. Source incident reference per row (links to A.5.26 incident register)

<<MUST item:A.5.28:reg_source_incident>>
_Why: Closes loop with [[A.5.26]]_

<<TEXT>>

## 3. Evidence type per row (log export / disk image / memory capture / physical media / statement / photograph)

<<MUST item:A.5.28:reg_evidence_type>>
_Why: 27002:5.28 — categorisation_

<<TEXT>>

## 4. Acquisition hash per row (cryptographic fingerprint recorded at point of collection)

<<MUST item:A.5.28:reg_acquisition_hash>>
_Why: 27002:5.28 — integrity_

<<TEXT>>

## 5. Current custodian per row (named individual or sealed-storage location)

<<MUST item:A.5.28:reg_custodian>>
_Why: 27002:5.28 — preservation_

<<TEXT>>

## 6. Current location per row (vault id / cloud bucket reference / external-party receipt id)

<<MUST item:A.5.28:reg_location>>
_Why: 27002:5.28 — storage_

<<TEXT>>

## 7. Status per row (active / handed-over / disposed) with date of last transition

<<MUST item:A.5.28:reg_status>>
_Why: Operational discipline_

<<TEXT>>

## 8. Retention end-date per row (drives the disposal_record trigger)

<<MUST item:A.5.28:reg_retention_end>>
_Why: 27002:5.28 — preservation lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-handover signature trail (immutable append-only — every transfer logs both releasing and receiving custodian)

<<SHOULD item:A.5.28:reg_handover_log>>
_Why: Forensic best practice_

<<TEXT>>

### 2. Jurisdiction tag per row where evidence may cross borders (drives admissibility considerations)

<<SHOULD item:A.5.28:reg_jurisdiction>>
_Why: Multi-jurisdiction handling_

<<TEXT>>
