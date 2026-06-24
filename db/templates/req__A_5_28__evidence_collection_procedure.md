---
leaf_id: req:A.5.28:evidence_collection_procedure
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Evidence Identification, Collection, Acquisition, and Preservation Procedure

> A.5.28 requires procedures for identification, collection, acquisition, and preservation of evidence related to information security events. The procedure documents the four lifecycle steps (identification → acquisition → preservation → handover/disposal), chain of custody enforcement, integrity verification, competent personnel requirements, and liaison paths with external authorities (law enforcement, regulators). The custody register, periodic program review and per-package disposal record are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Identification step (what counts as evidence — logs, images, physical media, witness statements, network captures)

<<MUST item:A.5.28:identification>>
_Why: 27002:5.28 — identification_

<<TEXT>>

## 2. Acquisition method per evidence type (disk imaging, log export, memory capture, photographic, statement)

<<MUST item:A.5.28:acquisition>>
_Why: 27002:5.28 — acquisition_

<<TEXT>>

## 3. Integrity verification step (cryptographic hashes recorded at acquisition; verified at each custody handover)

<<MUST item:A.5.28:integrity>>
_Why: 27002:5.28 — preservation_

<<TEXT>>

## 4. Chain-of-custody enforcement (who, what, when, where stored, signature/handover record at every transfer)

<<MUST item:A.5.28:chain_of_custody>>
_Why: 27002:5.28 — preservation_

<<TEXT>>

## 5. Preservation method (read-only/write-blocked storage, secure vault, environmental controls)

<<MUST item:A.5.28:preservation>>
_Why: 27002:5.28 — preservation_

<<TEXT>>

## 6. Competent personnel requirements (who is authorised to collect/handle evidence; certification expectations)

<<MUST item:A.5.28:competence>>
_Why: 27002:5.28 — internal procedures + competence_

<<TEXT>>

## 7. Liaison path with external authorities (law enforcement, regulators) — who initiates, what is required

<<MUST item:A.5.28:liaison>>
_Why: 27002:5.28 — external authorities_

<<TEXT>>

## 8. Retention period stated, driven by legal/regulatory obligations and case status (open investigations override default schedule)

<<MUST item:A.5.28:retention>>
_Why: 27002:5.28 — preservation lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Legal admissibility considerations (jurisdictional rules, multi-jurisdiction scenarios)

<<SHOULD item:A.5.28:legal_admissibility>>
_Why: Evidence usable in court / regulatory_

<<TEXT>>

### 2. Third-party forensic engagement path (when to engage, sealed-container handover, return-to-custody on completion)

<<SHOULD item:A.5.28:third_party_forensics>>
_Why: Operational flexibility_

<<TEXT>>

### 3. Cross-reference to A.5.26 incident-response procedure (evidence-collection step at containment)

<<SHOULD item:A.5.28:incident_link>>
_Why: Closing the loop with [[A.5.26]]_

<<TEXT>>
