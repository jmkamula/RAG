---
leaf_id: req:A.5.32:ipr_audit_review
control_ref: A.5.32
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic IPR and Licence Audit

> Periodic audit reconciling deployed software / used content against the inventory and licence entitlements. Catches drift the intake and procedure leaves miss — over-deployment of seat-limited licences, expired licences still in use, missing attribution, undeclared open-source components

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Audit date within the planned interval (typically annual; more frequent if a vendor audit risk is high)

<<MUST item:A.5.32:audit_cadence>>
_Why: Drift prevention_

<<TEXT>>

## 2. Reviewer identity and role (procurement / legal / engineering)

<<MUST item:A.5.32:audit_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Entitlement check — deployed seats/cores vs licence allowance per commercial entry, exceptions remediated

<<MUST item:A.5.32:audit_entitlement>>
_Why: 27002:5.32 — protect_

<<TEXT>>

## 4. Open-source attribution and licence-obligation check (NOTICE files, source-availability where required)

<<MUST item:A.5.32:audit_opensource>>
_Why: 27002:5.32 — third-party IPR_

<<TEXT>>

## 5. Expired/expiring licences flagged and renewal or removal completed

<<MUST item:A.5.32:audit_expiry>>
_Why: Continuity / drift_

<<TEXT>>

## 6. Inventory updated as a result of the audit with reference to this review

<<MUST item:A.5.32:audit_inventory_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Disposal of unused licences considered (cost optimisation alongside compliance)

<<SHOULD item:A.5.32:audit_dr_test>>
_Why: Adjacent value_

<<TEXT>>

### 2. Next planned audit date stated

<<SHOULD item:A.5.32:audit_next_date>>
_Why: Planning_

<<TEXT>>
