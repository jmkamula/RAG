---
leaf_id: req:A.8.4:source_code_access_procedure
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Source Code Access Procedure

<<DOC_CONTROL>>

> Operational counterpart to the baseline. Documents repo provisioning, dependency allowlist management, offboarding, exception handling

## What this template gives you

This template helps you clearly document how your team manages access to source code, including repository setup, dependency approvals, offboarding, and handling exceptions. It's designed to support operational security and compliance needs.

## When to use it

Use this procedure when your organization needs to formalize or update how source code access is granted, managed, and revoked—especially if your profile matches certain compliance triggers. Review and refresh the document whenever there are significant changes or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this template from scratch, as each required section takes roughly 10 to 15 minutes to fill out thoughtfully.

## 1. Repository provisioning procedure (creator authority, default branch-protection, classification)

<<MUST item:A.8.4:proc_repo_provisioning>>
_Why: 27002:8.4 — appropriately managed_

<<GUIDANCE>>

<<TEXT>>

## 2. Dependency allowlist process (new library → security review → approval)

<<MUST item:A.8.4:proc_dependency_allowlist>>
_Why: 27002:8.4 — software libraries_

<<GUIDANCE>>

<<TEXT>>

## 3. Repository access offboarding aligned with A.5.16 identity termination

<<MUST item:A.8.4:proc_offboarding>>
_Why: Common gap_

<<GUIDANCE>>

<<TEXT>>

## 4. Exception process for one-off elevated access (emergency hotfix authority)

<<MUST item:A.8.4:proc_exception>>
_Why: Operational flexibility_

<<GUIDANCE>>

<<TEXT>>

## 5. Secrets-rotation procedure where exposed (response within hours, not days)

<<MUST item:A.8.4:proc_secrets_rotation>>
_Why: Modern baseline_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Engineering lead with InfoSec partner)

<<SHOULD item:A.8.4:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
