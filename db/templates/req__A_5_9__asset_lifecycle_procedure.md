---
leaf_id: req:A.5.9:asset_lifecycle_procedure
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Asset Lifecycle Management Procedure

<<DOC_CONTROL>>

> A.5.9 requires the register to be maintained — the lifecycle procedure documents how assets enter, change and leave the register. Covers procurement intake, ownership transfer, classification at creation/change, retirement and disposal handoff (A.7.14 / A.8.10)

## What this template gives you

This template helps you clearly document how assets are added, updated, and removed from your asset register, ensuring you meet ISO 27001 requirements for asset lifecycle management.

## When to use it

Use this procedure whenever you need to describe how assets are managed throughout their lifecycle in your environment. Update it whenever your asset management processes change or new types of assets are introduced.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this from scratch, depending on the complexity of your asset management process and the number of asset types you handle.

## 1. Intake path — every new asset (procured, built, granted) is registered before going operational

<<MUST item:A.5.9:proc_intake>>
_Why: 27002:5.9 — develop_

<<GUIDANCE>>

<<TEXT>>

## 2. Ownership assignment rules (who can be an owner, transfer process on role change)

<<MUST item:A.5.9:proc_ownership>>
_Why: 27002:5.9d / Clause 5.3_

<<GUIDANCE>>

<<TEXT>>

## 3. Classification at creation and on material change (cross-link to A.5.12)

<<MUST item:A.5.9:proc_classification>>
_Why: 27002:5.9c / A.5.12_

<<GUIDANCE>>

<<TEXT>>

## 4. Retirement and disposal handoff (status set to retired, disposal handled per A.7.14/A.8.10, register row archived)

<<MUST item:A.5.9:proc_retirement>>
_Why: 27002:5.9 / A.7.14 / A.8.10_

<<GUIDANCE>>

<<TEXT>>

## 5. Named maintainer of the register and escalation path when intake fails

<<MUST item:A.5.9:proc_maintainer>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Shadow-IT handling — unregistered assets discovered in scans are blocked, registered, or removed

<<SHOULD item:A.5.9:proc_shadow_it>>
_Why: Drift prevention_

<<GUIDANCE>>

<<TEXT>>

### 2. Cloud-provisioning hooks (IaC pipelines auto-register infra; manual creations require a register entry first)

<<SHOULD item:A.5.9:proc_cloud_provision>>
_Why: Cloud completeness_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
