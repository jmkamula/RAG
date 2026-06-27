---
leaf_id: req:A.6.7:remote_workers_register
control_ref: A.6.7
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Approved Remote Workers Register

> Per-worker authoritative list of who is currently approved for remote working, with what conditions, on what equipment. The audit-defensibility surface for 'show me every active remote worker, when they were approved, and whether the approval is current'. Cross-references the A.5.16 identity register (every remote worker is also a registered identity) and the A.5.9 asset register (corporate equipment issued to them)

<!-- TABLE-COLUMNS leaf:req:A.6.7:remote_workers_register -->
<!-- column: item:A.6.7:reg_personnel_id -->
<!-- column: item:A.6.7:reg_approval_date -->
<!-- column: item:A.6.7:reg_location_category -->
<!-- column: item:A.6.7:reg_equipment_id -->
<!-- column: item:A.6.7:reg_conditions_summary -->
<!-- column: item:A.6.7:reg_review_due -->
<!-- column: item:A.6.7:reg_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.7:remote_workers_register -->
| Reg Personnel Id | Reg Approval Date | Reg Location Category | Reg Equipment Id | Reg Conditions Summary | Reg Review Due | Reg Status |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.7:remote_workers_register -->

## Column guidance — what to fill in

### Reg Personnel Id

<<MUST item:A.6.7:reg_personnel_id>>
_Why: Accountability + A.5.16 link_

> _Standard text:_ Per-row personnel identifier (links to A.5.16 identity register)

### Reg Approval Date

<<MUST item:A.6.7:reg_approval_date>>
_Why: 27002:6.7 — controlled approval_

> _Standard text:_ Per-row approval date + approving manager identity (closes 'who said yes')

### Reg Location Category

<<MUST item:A.6.7:reg_location_category>>
_Why: 27002:6.7b + GDPR_

> _Standard text:_ Per-row location category (home / co-working / abroad — drives jurisdictional risk; affects data-residency analysis where the worker handles personal data)

### Reg Equipment Id

<<MUST item:A.6.7:reg_equipment_id>>
_Why: 27002:6.7 — equipment + A.5.9 link_

> _Standard text:_ Per-row issued-equipment identifier (links to A.5.9 asset register; if BYOD, MDM-enrolment id)

### Reg Conditions Summary

<<MUST item:A.6.7:reg_conditions_summary>>
_Why: 27002:6.7 — appropriate conditions_

> _Standard text:_ Per-row conditions summary (permitted hours, data-class restrictions, expiry date, supervision requirements)

### Reg Review Due

<<MUST item:A.6.7:reg_review_due>>
_Why: 27002:6.7 — periodic re-evaluation_

> _Standard text:_ Per-row next-review-due date (drives the periodic review's expected-set computation; typically 12 months from approval)

### Reg Status

<<MUST item:A.6.7:reg_status>>
_Why: Operational discipline_

> _Standard text:_ Per-row status (active / suspended / expired-pending-revocation / revoked) — drives the leaver pair-check vs A.5.18 access register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Data Class Max

<<SHOULD item:A.6.7:reg_data_class_max>>
_Why: A.5.12 link_

> _Standard text:_ Per-row maximum data classification permitted (links to A.5.12 classification scheme — drives 'restricted-class data must not leave the office' enforcement)

### Reg Orphan Check

<<SHOULD item:A.6.7:reg_orphan_check>>
_Why: Continual assurance_

> _Standard text:_ Orphan-row check: any row whose personnel_id is no longer in A.5.16 active identity register (caught at periodic review) — surfaces missed leaver-flow revocations
