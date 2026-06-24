---
leaf_id: req:A.8.28:secure_coding_procedure
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Secure Coding Procedure

> A.8.28 requires secure-coding principles applied. Procedure documents language-specific standards, common-vulnerability prevention, code-review gates, automated analysis, secrets management. Per-finding register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Language-specific coding standards published (Python / Java / JavaScript / Go / C/C++ / Rust as applicable)

<<MUST item:A.8.28:language_standards>>
_Why: 27002:8.28 — secure coding principles_

<<TEXT>>

## 2. Common-vulnerability prevention guidance (OWASP Top 10 / CWE Top 25 mapped to language patterns)

<<MUST item:A.8.28:vulnerability_prevention>>
_Why: 27002:8.28 — secure coding_

<<TEXT>>

## 3. Code-review requirement before merge for production code (cross-link to A.8.4 branch protection)

<<MUST item:A.8.28:code_review>>
_Why: 27002:8.28 — applied_

<<TEXT>>

## 4. Automated static analysis (SAST) in CI pipeline (blocking severity threshold)

<<MUST item:A.8.28:sast>>
_Why: 27002:8.28 — applied_

<<TEXT>>

## 5. Secrets management — no secrets in code; vaulting + pre-commit scanning required

<<MUST item:A.8.28:secrets_in_code>>
_Why: 27002:8.28 — secure coding_

<<TEXT>>

## 6. SCA / dependency scanning enabled (modern baseline — supply-chain attack vector)

<<MUST item:A.8.28:dependency_scanning>>
_Why: Supply-chain hygiene (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure-coding training for developers (cross-link to A.6.3)

<<SHOULD item:A.8.28:training>>
_Why: People dimension_

<<TEXT>>
