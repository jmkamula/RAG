---
leaf_id: req:A.8.24:key_register
control_ref: A.8.24
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Cryptographic Key Register

> Per-key catalogue — key id, purpose, algorithm + strength, custodian, lifecycle dates. Drives 'every active key complies with current approved-algorithms table' audit

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row unique key identifier

<<MUST item:A.8.24:reg_key_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row purpose (encryption-at-rest / TLS / signing / KEK / DEK / token-signing)

<<MUST item:A.8.24:reg_purpose>>
_Why: 27002:8.24 — effective use_

<<TEXT>>

## 3. Per-row algorithm + strength (must match policy's approved-algorithms table)

<<MUST item:A.8.24:reg_algorithm>>
_Why: 27002:8.24a_

<<TEXT>>

## 4. Per-row custodian (HSM / KMS / split-knowledge custodians)

<<MUST item:A.8.24:reg_custodian>>
_Why: 27002:8.24b_

<<TEXT>>

## 5. Per-row lifecycle dates (generated / activated / next-rotation / retirement)

<<MUST item:A.8.24:reg_lifecycle_dates>>
_Why: 27002:8.24b_

<<TEXT>>

## 6. Per-row PII-key flag (drives stricter custody / GDPR Art.32 traceability)

<<MUST item:A.8.24:reg_pii_flag>>
_Why: GDPR Art.32_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row rotation-status flag (overdue / within-window / not-due)

<<SHOULD item:A.8.24:reg_rotation_status>>
_Why: Drift detection_

<<TEXT>>
