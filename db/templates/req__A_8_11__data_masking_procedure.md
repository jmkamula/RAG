---
leaf_id: req:A.8.11:data_masking_procedure
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Data Masking Procedure

> A.8.11 requires masking procedures for personal data in non-production environments. Procedure documents masking techniques, scope, roles. Per-application masking register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope — which systems/environments require masking (cross-link to A.5.12 classification + A.8.31 environment separation)

<<MUST item:A.8.11:scope>>
_Why: 27002:8.11 — appropriate use / SPEC_ART_25 reference_

<<TEXT>>

## 2. Masking techniques approved (static / dynamic / tokenisation / pseudonymisation / synthetic data)

<<MUST item:A.8.11:techniques>>
_Why: 27002:8.11 — applicable techniques / SPEC_ART_25 reference_

<<TEXT>>

## 3. Personal data explicitly in scope including PII / sensitive PII categories

<<MUST item:A.8.11:personal_data>>
_Why: 27002:8.11 / GDPR Art.32 / SPEC_ART_25 reference_

<<TEXT>>

## 4. Non-production environments explicitly covered (dev / test / staging / training / demo)

<<MUST item:A.8.11:non_production>>
_Why: Primary use case_

<<TEXT>>

## 5. Roles responsible (Engineering owners applying masking; DPO oversight for PII)

<<MUST item:A.8.11:roles>>
_Why: Accountability_

<<TEXT>>

## 6. Reversibility rules — when re-identification is permitted (none in non-prod by default; documented exceptions)

<<MUST item:A.8.11:reversibility_rules>>
_Why: Common attack vector_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Verification that masking is effective (sampling for re-identification residual risk)

<<SHOULD item:A.8.11:testing>>
_Why: Quality assurance_

<<TEXT>>

### 2. Exception process for unmasked data (e.g. live-production debugging) with time-limited authorisation

<<SHOULD item:A.8.11:exceptions>>
_Why: Governance_

<<TEXT>>
