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

> A.8.3 requires access to information and associated assets to be restricted per the topic-specific access control policy (A.5.15). The procedure documents enforcement mechanism, authorisation workflow, and recertification cadence. The access matrix register, applicable-scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Enforcement mechanism per system (ACL / RBAC / ABAC / IdP claims)

<<MUST item:A.8.3:enforcement>>
_Why: 27002:8.3 — restricted_

<<TEXT>>

## 2. Cross-link to A.5.15 access control policy + A.5.16 identity management

<<MUST item:A.8.3:policy_link>>
_Why: 27002:8.3 — accordance with topic-specific policy_

<<TEXT>>

## 3. Authorisation workflow for granting / changing / revoking access

<<MUST item:A.8.3:authorisation>>
_Why: 27002:8.3 — restricted_

<<TEXT>>

## 4. Periodic recertification cadence per system (cross-link to A.5.18)

<<MUST item:A.8.3:recertification>>
_Why: Drift prevention_

<<TEXT>>

## 5. Classification-driven restriction (sensitive info → stronger enforcement)

<<MUST item:A.8.3:classification_driven>>
_Why: 27002:8.3 — appropriate_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cloud / SaaS app permissions covered (IAM, SCIM provisioning)

<<SHOULD item:A.8.3:cloud_extensions>>
_Why: Modern environment_

<<TEXT>>
