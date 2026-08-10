---
leaf_id: req:A.8.3:information_access_restriction_procedure
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Information Access Restriction Procedure

<<DOC_CONTROL>>

> A.8.3 requires access to information and associated assets to be restricted per the topic-specific access control policy (A.5.15). The procedure documents enforcement mechanism, authorisation workflow, and recertification cadence. The access matrix register, applicable-scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how access to information and related assets is restricted and managed, including authorization steps and regular reviews. It supports compliance with ISO 27001 requirements for access control procedures.

## When to use it

Use this whenever you need to define or update your process for restricting access to information in your environment. Review and refresh the document as your procedures or access needs change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this from scratch, depending on the complexity of your access controls and the number of assets or users involved.

## 1. Enforcement mechanism per system (ACL / RBAC / ABAC / IdP claims)

<<MUST item:A.8.3:enforcement>>
_Why: 27002:8.3 — restricted_

<<GUIDANCE>>

<<TEXT>>

## 2. Cross-link to A.5.15 access control policy + A.5.16 identity management

<<MUST item:A.8.3:policy_link>>
_Why: 27002:8.3 — accordance with topic-specific policy_

<<GUIDANCE>>

<<TEXT>>

## 3. Authorisation workflow for granting / changing / revoking access

<<MUST item:A.8.3:authorisation>>
_Why: 27002:8.3 — restricted_

<<GUIDANCE>>

<<TEXT>>

## 4. Periodic recertification cadence per system (cross-link to A.5.18)

<<MUST item:A.8.3:recertification>>
_Why: Drift prevention_

<<GUIDANCE>>

<<TEXT>>

## 5. Classification-driven restriction (sensitive info → stronger enforcement)

<<MUST item:A.8.3:classification_driven>>
_Why: 27002:8.3 — appropriate_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cloud / SaaS app permissions covered (IAM, SCIM provisioning)

<<SHOULD item:A.8.3:cloud_extensions>>
_Why: Modern environment_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
