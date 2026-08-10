---
leaf_id: req:A.5.11:return_of_assets_procedure
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Return of Assets Procedure

<<DOC_CONTROL>>

> A.5.11 requires personnel to return all organisational assets upon change or termination. The procedure documents the trigger events, asset checklist (physical + logical), verification step, data preservation and wipe, role accountability and exception handling. The leaver register, periodic program review and per-leaver return record are sibling leaves

## What this template gives you

This template helps you create a clear process for making sure all company assets are returned when someone leaves or changes roles. It covers everything from asset checklists to data wiping and exception handling.

## When to use it

Use this whenever an employee or contractor leaves your organization or changes roles, to ensure all assets are accounted for. Review and update the procedure whenever your processes or asset lists change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this from scratch, depending on how many types of assets and steps you need to cover.

## 1. Triggers enumerated (termination, role change, contract end, change of agreement, end of secondment)

<<MUST item:A.5.11:triggers>>
_Why: 27002:5.11 — upon change or termination_

<<GUIDANCE>>

<<TEXT>>

## 2. Checklist of asset types to be returned — physical (laptops, mobile devices, badges, tokens) and logical (corp credentials, data on personal devices)

<<MUST item:A.5.11:asset_checklist>>
_Why: 27002:5.11 — all organizational assets_

<<GUIDANCE>>

<<TEXT>>

## 3. Verification step signed by both the returning party and the receiving role (IT/manager) with itemised confirmation

<<MUST item:A.5.11:verification>>
_Why: 27002:5.11 — return_

<<GUIDANCE>>

<<TEXT>>

## 4. Data preservation step BEFORE wipe (org information on the asset must be captured / migrated, not just deleted)

<<MUST item:A.5.11:data_preservation>>
_Why: 27002:5.11 — preservation of organisational information_

<<GUIDANCE>>

<<TEXT>>

## 5. Data wipe / sanitisation step for assets carrying organisational information (cross-link to A.8.10 deletion)

<<MUST item:A.5.11:data_handling>>
_Why: 27002:5.11 — data handling + cross-link to [[A.8.10]]_

<<GUIDANCE>>

<<TEXT>>

## 6. Owner of the procedure (typically HR + IT joint with InfoSec sign-off authority)

<<MUST item:A.5.11:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## 7. Non-return path defined (when assets cannot be physically returned — remote staff, lost device, contractor dispute — alternative attestation + risk acceptance)

<<MUST item:A.5.11:non_return_path>>
_Why: 27002:5.11 — risk-based handling of unreturned items_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Timeline stated (e.g. assets returned by last working day; data return ahead of access revocation)

<<SHOULD item:A.5.11:timeline>>
_Why: Timeliness_

<<GUIDANCE>>

<<TEXT>>

### 2. Exception process for outstanding assets (work-from-home, contractor delays, lost-in-transit)

<<SHOULD item:A.5.11:exception_process>>
_Why: Real-world friction_

<<GUIDANCE>>

<<TEXT>>

### 3. Contractor variant documented where standard employee path doesn't apply (third-party offboarding, project closure)

<<SHOULD item:A.5.11:contractor_variant>>
_Why: Workforce-model coverage_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
