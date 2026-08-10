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

<<DOC_CONTROL>>

> A.8.11 requires masking procedures for personal data in non-production environments. Procedure documents masking techniques, scope, roles. Per-application masking register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document how personal data is masked in non-production environments, including the techniques used, the scope, and the roles involved. It also provides a structure for tracking masking activities per application.

## When to use it

Use this template whenever your organization handles personal data in test or development environments, and update it whenever your masking procedures or scope change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this template from scratch, depending on the number of applications and the complexity of your data masking processes.

## 1. Scope — which systems/environments require masking (cross-link to A.5.12 classification + A.8.31 environment separation)

<<MUST item:A.8.11:scope>>
_Why: 27002:8.11 — appropriate use / SPEC_ART_25 reference_

<<GUIDANCE>>

<<TEXT>>

## 2. Masking techniques approved (static / dynamic / tokenisation / pseudonymisation / synthetic data)

<<MUST item:A.8.11:techniques>>
_Why: 27002:8.11 — applicable techniques / SPEC_ART_25 reference_

<<GUIDANCE>>

<<TEXT>>

## 3. Personal data explicitly in scope including PII / sensitive PII categories

<<MUST item:A.8.11:personal_data>>
_Why: 27002:8.11 / GDPR Art.32 / SPEC_ART_25 reference_

<<GUIDANCE>>

<<TEXT>>

## 4. Non-production environments explicitly covered (dev / test / staging / training / demo)

<<MUST item:A.8.11:non_production>>
_Why: Primary use case_

<<GUIDANCE>>

<<TEXT>>

## 5. Roles responsible (Engineering owners applying masking; DPO oversight for PII)

<<MUST item:A.8.11:roles>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## 6. Reversibility rules — when re-identification is permitted (none in non-prod by default; documented exceptions)

<<MUST item:A.8.11:reversibility_rules>>
_Why: Common attack vector_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Verification that masking is effective (sampling for re-identification residual risk)

<<SHOULD item:A.8.11:testing>>
_Why: Quality assurance_

<<GUIDANCE>>

<<TEXT>>

### 2. Exception process for unmasked data (e.g. live-production debugging) with time-limited authorisation

<<SHOULD item:A.8.11:exceptions>>
_Why: Governance_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
