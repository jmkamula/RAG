---
leaf_id: req:A.8.24:key_register
control_ref: A.8.24
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Cryptographic Key Register

<<DOC_CONTROL>>

> Per-key catalogue — key id, purpose, algorithm + strength, custodian, lifecycle dates. Drives 'every active key complies with current approved-algorithms table' audit

<!-- TABLE-COLUMNS leaf:req:A.8.24:key_register -->
<!-- column: item:A.8.24:reg_key_id -->
<!-- column: item:A.8.24:reg_purpose -->
<!-- column: item:A.8.24:reg_algorithm -->
<!-- column: item:A.8.24:reg_custodian -->
<!-- column: item:A.8.24:reg_lifecycle_dates -->
<!-- column: item:A.8.24:reg_pii_flag -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your cryptographic keys, including details like their purpose, algorithm, and custodian. It supports audits by showing that your keys follow approved security standards.

## When to use it

Use this register at all times in your environment to track every active cryptographic key, updating it whenever you add, change, or retire a key to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10–15 minutes per key for each required detail when setting up the register from scratch, with total time depending on how many keys you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.24:key_register -->
| Reg Key Id | Reg Purpose | Reg Algorithm | Reg Custodian | Reg Lifecycle Dates | Reg Pii Flag |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.24:key_register -->

## Column guidance — what to fill in

### Reg Key Id

<<MUST item:A.8.24:reg_key_id>>
_Why: Identification_

> _Standard text:_ Per-row unique key identifier

<<GUIDANCE>>

### Reg Purpose

<<MUST item:A.8.24:reg_purpose>>
_Why: 27002:8.24 — effective use_

> _Standard text:_ Per-row purpose (encryption-at-rest / TLS / signing / KEK / DEK / token-signing)

<<GUIDANCE>>

### Reg Algorithm

<<MUST item:A.8.24:reg_algorithm>>
_Why: 27002:8.24a_

> _Standard text:_ Per-row algorithm + strength (must match policy's approved-algorithms table)

<<GUIDANCE>>

### Reg Custodian

<<MUST item:A.8.24:reg_custodian>>
_Why: 27002:8.24b_

> _Standard text:_ Per-row custodian (HSM / KMS / split-knowledge custodians)

<<GUIDANCE>>

### Reg Lifecycle Dates

<<MUST item:A.8.24:reg_lifecycle_dates>>
_Why: 27002:8.24b_

> _Standard text:_ Per-row lifecycle dates (generated / activated / next-rotation / retirement)

<<GUIDANCE>>

### Reg Pii Flag

<<MUST item:A.8.24:reg_pii_flag>>
_Why: GDPR Art.32_

> _Standard text:_ Per-row PII-key flag (drives stricter custody / GDPR Art.32 traceability)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Rotation Status

<<SHOULD item:A.8.24:reg_rotation_status>>
_Why: Drift detection_

> _Standard text:_ Per-row rotation-status flag (overdue / within-window / not-due)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
