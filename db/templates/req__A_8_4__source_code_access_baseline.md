---
leaf_id: req:A.8.4:source_code_access_baseline
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Source Code Access Baseline

> A.8.4 baseline — repository configuration state. Defines the RBAC model, branch protection, secrets scanning, dependency rules. profile_fact trigger because A.8.4 only applies where the organisation develops software. The procedure, monitoring log and review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. RBAC configured per repository (read / write / admin) at the platform level

<<MUST item:A.8.4:bl_rbac>>
_Why: 27002:8.4 — read and write access_

<<TEXT>>

## 2. Branch protection enabled on protected branches (review required, status checks required)

<<MUST item:A.8.4:bl_branch_protection>>
_Why: 27002:8.4 — appropriately managed_

<<TEXT>>

## 3. Secrets scanning active on commit + push (pre-commit hook or platform scanner)

<<MUST item:A.8.4:bl_secrets_scanning>>
_Why: 27002:8.4 — appropriately managed_

<<TEXT>>

## 4. Dependency vulnerability scanning active per repository (SCA tool integrated)

<<MUST item:A.8.4:bl_dependency_scanning>>
_Why: 27002:8.4 — software libraries_

<<TEXT>>

## 5. CI/CD systems access restricted to authorised roles (cross-link to A.8.31 environment separation)

<<MUST item:A.8.4:bl_ci_isolation>>
_Why: 27002:8.4 — development tools_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Commit signing enforced for protected branches

<<SHOULD item:A.8.4:bl_signed_commits>>
_Why: Supply chain hygiene_

<<TEXT>>
