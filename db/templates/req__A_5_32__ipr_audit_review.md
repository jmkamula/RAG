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
table_shape: true
---

# Periodic IPR and Licence Audit

> Periodic audit reconciling deployed software / used content against the inventory and licence entitlements. Catches drift the intake and procedure leaves miss — over-deployment of seat-limited licences, expired licences still in use, missing attribution, undeclared open-source components

<!-- TABLE-COLUMNS leaf:req:A.5.32:ipr_audit_review -->
<!-- column: item:A.5.32:audit_cadence -->
<!-- column: item:A.5.32:audit_reviewer -->
<!-- column: item:A.5.32:audit_entitlement -->
<!-- column: item:A.5.32:audit_opensource -->
<!-- column: item:A.5.32:audit_expiry -->
<!-- column: item:A.5.32:audit_inventory_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.32:ipr_audit_review -->
| Audit Cadence | Audit Reviewer | Audit Entitlement | Audit Opensource | Audit Expiry | Audit Inventory Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.32:ipr_audit_review -->

## Column guidance — what to fill in

### Audit Cadence

<<MUST item:A.5.32:audit_cadence>>
_Why: Drift prevention_

> _Standard text:_ Audit date within the planned interval (typically annual; more frequent if a vendor audit risk is high)

### Audit Reviewer

<<MUST item:A.5.32:audit_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (procurement / legal / engineering)

### Audit Entitlement

<<MUST item:A.5.32:audit_entitlement>>
_Why: 27002:5.32 — protect_

> _Standard text:_ Entitlement check — deployed seats/cores vs licence allowance per commercial entry, exceptions remediated

### Audit Opensource

<<MUST item:A.5.32:audit_opensource>>
_Why: 27002:5.32 — third-party IPR_

> _Standard text:_ Open-source attribution and licence-obligation check (NOTICE files, source-availability where required)

### Audit Expiry

<<MUST item:A.5.32:audit_expiry>>
_Why: Continuity / drift_

> _Standard text:_ Expired/expiring licences flagged and renewal or removal completed

### Audit Inventory Update

<<MUST item:A.5.32:audit_inventory_update>>
_Why: Closes the loop_

> _Standard text:_ Inventory updated as a result of the audit with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Audit Dr Test

<<SHOULD item:A.5.32:audit_dr_test>>
_Why: Adjacent value_

> _Standard text:_ Disposal of unused licences considered (cost optimisation alongside compliance)

### Audit Next Date

<<SHOULD item:A.5.32:audit_next_date>>
_Why: Planning_

> _Standard text:_ Next planned audit date stated
