---
leaf_id: req:A.5.18:access_rights_procedure
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Access Rights Management Procedure

> A.5.18 requires that access rights be provisioned, reviewed, modified and removed in accordance with the topic-specific policy on access control (A.5.15). The procedure documents the operational steps for grant, modification and revocation, the SLA targets for each operation, the handling of service accounts, and the linkage to identity management. The access rights register, periodic review and revocation record are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Asset owner authorization required before access is granted (named authoriser per asset class, not generic 'IT manager')

<<MUST item:A.5.18:asset_owner_authorization>>
_Why: 27002:5.18a_

<<TEXT>>

## 2. Provisioning applies least privilege and segregation-of-duties checks (cross-link to A.5.3 segregation of duties — flagged combinations are blocked or compensated)

<<MUST item:A.5.18:least_privilege>>
_Why: 27002:5.18b / A.5.3_

<<TEXT>>

## 3. References the topic-specific access control policy (A.5.15) — drives consistency between policy and operational practice

<<MUST item:A.5.18:policy_reference>>
_Why: 27002:5.18c / A.5.15_

<<TEXT>>

## 4. Path for modification of access on role or responsibility change (joiner-mover-leaver flows; mover is the typically-missed leg)

<<MUST item:A.5.18:modification_path>>
_Why: 27002:5.18g_

<<TEXT>>

## 5. Privileged access requests route through the A.8.2 privileged-access process (separate intake, separate approval, separate logging)

<<MUST item:A.5.18:privileged_route>>
_Why: 27002:5.18i / A.8.2_

<<TEXT>>

## 6. SLA targets stated per operation (grant within X days, modification within Y days, revocation within Z hours of trigger — drives the rev_sla_met flag on revocation_record)

<<MUST item:A.5.18:sla_targets>>
_Why: 27002:5.18d/g — timeliness_

<<TEXT>>

## 7. Service account / non-human identity handling stated (provisioning, owner attribution, periodic re-attestation — service accounts are the weakest spot in most access programs)

<<MUST item:A.5.18:service_account_handling>>
_Why: 27002:5.18 — all identity classes_

<<TEXT>>

## 8. Explicit linkage to A.5.16 identity management (every access right attaches to a registered identity; no orphan access)

<<MUST item:A.5.18:identity_link>>
_Why: A.5.16 coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Temporary access provisions for time-bound tasks or third parties (expiry date mandatory; automated revocation at expiry)

<<SHOULD item:A.5.18:temporary_access>>
_Why: 27002:5.18e_

<<TEXT>>

### 2. Retention period for approval evidence stated (drives the audit trail for who-approved-what-when)

<<SHOULD item:A.5.18:approval_retention>>
_Why: Accountability_

<<TEXT>>

### 3. Emergency-access ('break-glass') procedure stated separately (pre-approved accounts with mandatory post-use justification + audit)

<<SHOULD item:A.5.18:emergency_access>>
_Why: Operational realism_

<<TEXT>>
