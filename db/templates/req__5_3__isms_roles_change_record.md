---
leaf_id: req:5.3:isms_roles_change_record
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: change_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# ISMS Roles Change Record

<<DOC_CONTROL>>

> Per-change record capturing each amendment to the roles matrix — role added, role retired, role-holder changed. Lifecycle-end artefact proving role drift is being managed, not silent

<!-- TABLE-COLUMNS leaf:req:5.3:isms_roles_change_record -->
<!-- column: item:5.3:chg_trigger -->
<!-- column: item:5.3:chg_summary -->
<!-- column: item:5.3:chg_comms -->
<!-- column: item:5.3:chg_approval -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date record of every change made to your information security roles, making it easy to show that you are actively managing and tracking role assignments.

## When to use it

Use this record whenever you add, remove, or change a role or role-holder in your ISMS, and update it as often as changes occur to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required field for each change; for a single update, completing the register from scratch typically takes 40-60 minutes.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.3:isms_roles_change_record -->
| Chg Trigger | Chg Summary | Chg Comms | Chg Approval |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.3:isms_roles_change_record -->

## Column guidance — what to fill in

### Chg Trigger

<<MUST item:5.3:chg_trigger>>
_Why: Defensible amendment_

> _Standard text:_ Change trigger stated (org restructure, new control area, person change, new framework)

<<GUIDANCE>>

### Chg Summary

<<MUST item:5.3:chg_summary>>
_Why: Audit clarity_

> _Standard text:_ Change summary — what was added, removed, or reassigned

<<GUIDANCE>>

### Chg Comms

<<MUST item:5.3:chg_comms>>
_Why: Clause 5.3 — communicated_

> _Standard text:_ Communication of the change (link to 7.4) — affected role-holders informed

<<GUIDANCE>>

### Chg Approval

<<MUST item:5.3:chg_approval>>
_Why: Clause 5.3 — assigned_

> _Standard text:_ Approval signature with date (top management or delegated authority)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Chg A52 Check

<<SHOULD item:5.3:chg_a52_check>>
_Why: Cross-control coherence_

> _Standard text:_ A.5.2 operational-roles cross-check captured (where 5.3 and A.5.2 touch)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
