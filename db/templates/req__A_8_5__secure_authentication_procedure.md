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

> Operational counterpart — credential issuance, factor enrolment, recovery flow, exception handling. Cross-link to A.5.17 authentication info lifecycle

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Factor enrolment procedure (initial MFA setup, with identity-proofing strength matched to tier)

<<MUST item:A.8.5:proc_enrolment>>
_Why: 27002:8.5 — implemented_

<<TEXT>>

## 2. Account recovery flow with identity-proofing (NOT password reset via email-only)

<<MUST item:A.8.5:proc_recovery>>
_Why: Common attack vector_

<<TEXT>>

## 3. Cross-link to A.5.17 authentication info procedure (credential rotation, revocation)

<<MUST item:A.8.5:proc_a517_linkage>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Exception process for lost-MFA / new-device scenarios with identity-proofing fallback

<<MUST item:A.8.5:proc_exception>>
_Why: Operational reality_

<<TEXT>>

## 5. Legacy protocol handling (rejection by default; documented exception with compensating controls)

<<MUST item:A.8.5:proc_legacy_handling>>
_Why: Common vulnerability path_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. User education on phishing-resistant authentication usage

<<SHOULD item:A.8.5:proc_user_education>>
_Why: Detection support_

<<TEXT>>
