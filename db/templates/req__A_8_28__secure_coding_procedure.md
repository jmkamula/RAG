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

<<DOC_CONTROL>>

> A.8.28 requires secure-coding principles applied. Procedure documents language-specific standards, common-vulnerability prevention, code-review gates, automated analysis, secrets management. Per-finding register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document your secure coding practices, including language-specific standards, vulnerability prevention, code reviews, automated checks, and secrets management. It's designed to support compliance with ISO 27001 requirements for secure software development.

## When to use it

Use this template when your organization needs to demonstrate secure coding procedures, especially if your risk profile or regulatory requirements call for it. Update the document whenever your coding practices or related controls change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this from scratch, depending on the complexity of your coding environment and the number of findings or registers you need to include.

## 1. Language-specific coding standards published (Python / Java / JavaScript / Go / C/C++ / Rust as applicable)

<<MUST item:A.8.28:language_standards>>
_Why: 27002:8.28 — secure coding principles_

<<GUIDANCE>>

<<TEXT>>

## 2. Common-vulnerability prevention guidance (OWASP Top 10 / CWE Top 25 mapped to language patterns)

<<MUST item:A.8.28:vulnerability_prevention>>
_Why: 27002:8.28 — secure coding_

<<GUIDANCE>>

<<TEXT>>

## 3. Code-review requirement before merge for production code (cross-link to A.8.4 branch protection)

<<MUST item:A.8.28:code_review>>
_Why: 27002:8.28 — applied_

<<GUIDANCE>>

<<TEXT>>

## 4. Automated static analysis (SAST) in CI pipeline (blocking severity threshold)

<<MUST item:A.8.28:sast>>
_Why: 27002:8.28 — applied_

<<GUIDANCE>>

<<TEXT>>

## 5. Secrets management — no secrets in code; vaulting + pre-commit scanning required

<<MUST item:A.8.28:secrets_in_code>>
_Why: 27002:8.28 — secure coding_

<<GUIDANCE>>

<<TEXT>>

## 6. SCA / dependency scanning enabled (modern baseline — supply-chain attack vector)

<<MUST item:A.8.28:dependency_scanning>>
_Why: Supply-chain hygiene (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure-coding training for developers (cross-link to A.6.3)

<<SHOULD item:A.8.28:training>>
_Why: People dimension_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
