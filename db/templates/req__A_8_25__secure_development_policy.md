---
leaf_id: req:A.8.25:secure_development_policy
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 2
---

# Secure Development Lifecycle Policy

> A.8.25 requires rules for secure development. Policy states SDLC principles, environment requirements, version control, security-requirement integration, testing integration, personal-data handling. Per-project register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Security principles for software design (cross-link to A.8.27 architecture principles)

<<MUST item:A.8.25:principles>>
_Why: 27002:8.25a_

<<TEXT>>

## 2. Security of development environments (cross-link to A.8.31 environment separation)

<<MUST item:A.8.25:environments>>
_Why: 27002:8.25b_

<<TEXT>>

## 3. Version-control requirements (cross-link to A.8.4 source code access)

<<MUST item:A.8.25:versioning>>
_Why: 27002:8.25c_

<<TEXT>>

## 4. Security requirements integration (cross-link to A.8.26 — security requirements at design phase)

<<MUST item:A.8.25:security_req>>
_Why: A.8.26 linkage_

<<TEXT>>

## 5. Security testing integration (cross-link to A.8.29 — testing in lifecycle)

<<MUST item:A.8.25:testing>>
_Why: A.8.29 linkage_

<<TEXT>>

## 6. Handling of personal data in development / test environments (cross-link to A.8.11 masking — no real PII in non-production)

<<MUST item:A.8.25:personal_data>>
_Why: 27002:8.25 / GDPR Art.32_

<<TEXT>>

## 7. Named policy authority (Engineering lead with InfoSec partner)

<<MUST item:A.8.25:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure-coding training requirements (cross-link to A.8.28 + A.6.3)

<<SHOULD item:A.8.25:training>>
_Why: A.8.28 linkage_

<<TEXT>>

### 2. Code-review requirements (cross-link to A.8.4 branch protection)

<<SHOULD item:A.8.25:code_review>>
_Why: Quality assurance_

<<TEXT>>
