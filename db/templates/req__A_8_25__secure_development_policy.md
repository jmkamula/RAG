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

<<DOC_CONTROL>>

> A.8.25 requires rules for secure development. Policy states SDLC principles, environment requirements, version control, security-requirement integration, testing integration, personal-data handling. Per-project register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you create a clear policy for secure software development, covering key areas like version control, secure environments, and handling personal data. It's designed to help you meet ISO 27001 requirements for secure development practices.

## When to use it

Use this template when your organization develops software and needs to document secure development practices, especially if your risk profile or compliance requirements change. Update the policy as needed to stay current with your processes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this policy from scratch, depending on the complexity of your development environment and the number of projects you need to register.

## 1. Security principles for software design (cross-link to A.8.27 architecture principles)

<<MUST item:A.8.25:principles>>
_Why: 27002:8.25a_

<<GUIDANCE>>

<<TEXT>>

## 2. Security of development environments (cross-link to A.8.31 environment separation)

<<MUST item:A.8.25:environments>>
_Why: 27002:8.25b_

<<GUIDANCE>>

<<TEXT>>

## 3. Version-control requirements (cross-link to A.8.4 source code access)

<<MUST item:A.8.25:versioning>>
_Why: 27002:8.25c_

<<GUIDANCE>>

<<TEXT>>

## 4. Security requirements integration (cross-link to A.8.26 — security requirements at design phase)

<<MUST item:A.8.25:security_req>>
_Why: A.8.26 linkage_

<<GUIDANCE>>

<<TEXT>>

## 5. Security testing integration (cross-link to A.8.29 — testing in lifecycle)

<<MUST item:A.8.25:testing>>
_Why: A.8.29 linkage_

<<GUIDANCE>>

<<TEXT>>

## 6. Handling of personal data in development / test environments (cross-link to A.8.11 masking — no real PII in non-production)

<<MUST item:A.8.25:personal_data>>
_Why: 27002:8.25 / GDPR Art.32_

<<GUIDANCE>>

<<TEXT>>

## 7. Named policy authority (Engineering lead with InfoSec partner)

<<MUST item:A.8.25:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure-coding training requirements (cross-link to A.8.28 + A.6.3)

<<SHOULD item:A.8.25:training>>
_Why: A.8.28 linkage_

<<GUIDANCE>>

<<TEXT>>

### 2. Code-review requirements (cross-link to A.8.4 branch protection)

<<SHOULD item:A.8.25:code_review>>
_Why: Quality assurance_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
