---
leaf_id: req:A.8.24:cryptography_policy
control_ref: A.8.24
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 9
should_count: 2
---

# Use of Cryptography Policy

> A.8.24 requires a policy on effective use of cryptography. Policy states approved algorithms, key-management approach, at-rest + in-transit requirements, roles. Per-key register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Approved cryptographic algorithms with minimum strengths (per regulator/NIST/CNSA-compliant tables)

<<MUST item:A.8.24:algorithms>>
_Why: 27002:8.24a_

<<TEXT>>

## 2. Key-management principles defined (generation / storage / rotation / revocation / archival / destruction)

<<MUST item:A.8.24:key_mgmt>>
_Why: 27002:8.24b_

<<TEXT>>

## 3. Encryption requirements for data at rest per classification tier

<<MUST item:A.8.24:at_rest>>
_Why: 27002:8.24c / SPEC_ART_32 reference_

<<TEXT>>

## 4. Encryption requirements for data in transit per classification tier

<<MUST item:A.8.24:in_transit>>
_Why: 27002:8.24c / SPEC_ART_32 reference_

<<TEXT>>

## 5. Roles + responsibilities for cryptography (key custodian / approver / operator)

<<MUST item:A.8.24:roles>>
_Why: 27002:8.24e_

<<TEXT>>

## 6. Personal data explicitly scoped for encryption (GDPR Art.32.1a integration)

<<MUST item:A.8.24:personal_data>>
_Why: 27002:8.24 / GDPR Art.32 / SPEC_ART_32 reference_

<<TEXT>>

## 7. Key management for PII encryption keys (separation of duties / DPIA-required where applicable)

<<MUST item:A.8.24:pii_keys>>
_Why: GDPR Art.32 / SPEC_ART_32 reference_

<<TEXT>>

## 8. Key length / strength requirements stated (Style v2 promotion — was SHOULD)

<<MUST item:A.8.24:key_strength>>
_Why: 27002:8.24f_

<<TEXT>>

## 9. Named policy authority (InfoSec lead with Cryptography subject-matter expert)

<<MUST item:A.8.24:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exceptions process for legacy algorithms with compensating-control + retirement plan

<<SHOULD item:A.8.24:exceptions>>
_Why: Governance_

<<TEXT>>

### 2. Post-quantum cryptography direction (NIST PQC track — modern forward-looking baseline)

<<SHOULD item:A.8.24:pq_direction>>
_Why: Modern threat landscape_

<<TEXT>>
