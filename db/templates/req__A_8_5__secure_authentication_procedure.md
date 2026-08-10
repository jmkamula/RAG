---
leaf_id: req:A.8.5:secure_authentication_procedure
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Authentication Provisioning Procedure

<<DOC_CONTROL>>

> Operational counterpart — credential issuance, factor enrolment, recovery flow, exception handling. Cross-link to A.5.17 authentication info lifecycle

## What this template gives you

This template helps you document how your organization issues credentials, enrolls authentication factors, manages recovery processes, and handles exceptions related to user authentication. It ensures your procedures align with ISO 27001 requirements for authentication information.

## When to use it

Use this template whenever you need to establish or update your authentication provisioning procedures, as it should always be maintained for your environment and refreshed whenever there are changes to your processes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this template from scratch, as each required section typically takes 10 to 15 minutes to write.

## 1. Factor enrolment procedure (initial MFA setup, with identity-proofing strength matched to tier)

<<MUST item:A.8.5:proc_enrolment>>
_Why: 27002:8.5 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 2. Account recovery flow with identity-proofing (NOT password reset via email-only)

<<MUST item:A.8.5:proc_recovery>>
_Why: Common attack vector_

<<GUIDANCE>>

<<TEXT>>

## 3. Cross-link to A.5.17 authentication info procedure (credential rotation, revocation)

<<MUST item:A.8.5:proc_a517_linkage>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 4. Exception process for lost-MFA / new-device scenarios with identity-proofing fallback

<<MUST item:A.8.5:proc_exception>>
_Why: Operational reality_

<<GUIDANCE>>

<<TEXT>>

## 5. Legacy protocol handling (rejection by default; documented exception with compensating controls)

<<MUST item:A.8.5:proc_legacy_handling>>
_Why: Common vulnerability path_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. User education on phishing-resistant authentication usage

<<SHOULD item:A.8.5:proc_user_education>>
_Why: Detection support_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
