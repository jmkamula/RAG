---
leaf_id: req:A.8.2:privileged_access_procedure
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Privileged Access Management Procedure

<<DOC_CONTROL>>

> A.8.2 requires the allocation and use of privileged access rights to be restricted and managed on a need-to-use, event-by-event basis with formal authorisation. The procedure documents provisioning, use, expiry and deprovisioning of privileged access — the operational counterpart to the baseline

## What this template gives you

This template helps you document how privileged access is granted, used, and revoked in your organization, ensuring you meet ISO 27001 requirements for managing sensitive system permissions.

## When to use it

Use this procedure whenever your environment includes privileged accounts or elevated access, and update it whenever there are changes to how privileged access is managed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this template from scratch, depending on the complexity of your access management processes.

## 1. Privileged access granted on need-to-use, event-by-event basis (less than or equal to the period needed)

<<MUST item:A.8.2:proc_need_to_use>>
_Why: 27002:8.2b_

<<GUIDANCE>>

<<TEXT>>

## 2. Formal authorisation process before privileged access is granted or changed

<<MUST item:A.8.2:proc_authorisation>>
_Why: 27002:8.2c, i_

<<GUIDANCE>>

<<TEXT>>

## 3. Separate accounts mandated for administrative actions (admin account distinct from daily-use)

<<MUST item:A.8.2:proc_separate_accounts>>
_Why: 27002:8.2f_

<<GUIDANCE>>

<<TEXT>>

## 4. Expiry rules defined for privileged access rights

<<MUST item:A.8.2:proc_expiry>>
_Why: 27002:8.2d_

<<GUIDANCE>>

<<TEXT>>

## 5. Users acknowledge accountability for their privileged access (e.g. signed acceptable-use)

<<MUST item:A.8.2:proc_accountability>>
_Why: 27002:8.2e_

<<GUIDANCE>>

<<TEXT>>

## 6. Break-glass account governance (sealed credentials, post-use review)

<<MUST item:A.8.2:proc_break_glass>>
_Why: Emergency access without weak ongoing exposure_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Procedure prohibits routine non-privileged tasks under a privileged account

<<SHOULD item:A.8.2:proc_routine_separation>>
_Why: 27002:8.2f_

<<GUIDANCE>>

<<TEXT>>

### 2. Revocation path on role change / termination (links to A.5.18 revocation records)

<<SHOULD item:A.8.2:proc_revocation_path>>
_Why: A.5.18 linkage_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
