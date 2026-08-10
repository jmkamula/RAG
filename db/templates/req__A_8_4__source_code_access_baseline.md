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

<<DOC_CONTROL>>

> A.8.4 baseline — repository configuration state. Defines the RBAC model, branch protection, secrets scanning, dependency rules. profile_fact trigger because A.8.4 only applies where the organisation develops software. The procedure, monitoring log and review are sibling leaves

## What this template gives you

This template helps you document how your source code repositories are set up and protected, including who can access them, how branches are managed, and how secrets and dependencies are handled.

## When to use it

Use this template if your organization develops software and needs to show how you control access and security for your code repositories. Update it whenever your repository configuration changes or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, as each required section will take roughly 10 to 15 minutes to fill out.

## 1. RBAC configured per repository (read / write / admin) at the platform level

<<MUST item:A.8.4:bl_rbac>>
_Why: 27002:8.4 — read and write access_

<<GUIDANCE>>

<<TEXT>>

## 2. Branch protection enabled on protected branches (review required, status checks required)

<<MUST item:A.8.4:bl_branch_protection>>
_Why: 27002:8.4 — appropriately managed_

<<GUIDANCE>>

<<TEXT>>

## 3. Secrets scanning active on commit + push (pre-commit hook or platform scanner)

<<MUST item:A.8.4:bl_secrets_scanning>>
_Why: 27002:8.4 — appropriately managed_

<<GUIDANCE>>

<<TEXT>>

## 4. Dependency vulnerability scanning active per repository (SCA tool integrated)

<<MUST item:A.8.4:bl_dependency_scanning>>
_Why: 27002:8.4 — software libraries_

<<GUIDANCE>>

<<TEXT>>

## 5. CI/CD systems access restricted to authorised roles (cross-link to A.8.31 environment separation)

<<MUST item:A.8.4:bl_ci_isolation>>
_Why: 27002:8.4 — development tools_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Commit signing enforced for protected branches

<<SHOULD item:A.8.4:bl_signed_commits>>
_Why: Supply chain hygiene_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
