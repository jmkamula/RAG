---
leaf_id: req:4.3:scope_change_record
control_ref: 4.3
standard_id: ISO27001:2022
evidence_type: change_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# ISMS Scope Change Record

<<DOC_CONTROL>>

> Per-change record capturing each scope amendment — the lifecycle-end artefact that proves scope changes are deliberate and approved, not silent drift

<!-- TABLE-COLUMNS leaf:req:4.3:scope_change_record -->
<!-- column: item:4.3:chg_trigger -->
<!-- column: item:4.3:chg_summary -->
<!-- column: item:4.3:chg_impact -->
<!-- column: item:4.3:chg_approval -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly document every change to the scope of your information security management system, ensuring that all amendments are intentional, approved, and traceable for audit purposes.

## When to use it

Use this record whenever you make a change to your ISMS scope, and update it as needed whenever further changes occur. It applies continuously to your environment to prevent unnoticed scope drift.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required element takes around 10-15 minutes to fill in. Adding more changes over time will require additional entries.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.3:scope_change_record -->
| Chg Trigger | Chg Summary | Chg Impact | Chg Approval |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.3:scope_change_record -->

## Column guidance — what to fill in

### Chg Trigger

<<MUST item:4.3:chg_trigger>>
_Why: Defensible amendment_

> _Standard text:_ Change trigger stated (new site, divestment, new product line, new regulator)

<<GUIDANCE>>

### Chg Summary

<<MUST item:4.3:chg_summary>>
_Why: Audit clarity_

> _Standard text:_ Change summary — what was added or removed from scope

<<GUIDANCE>>

### Chg Impact

<<MUST item:4.3:chg_impact>>
_Why: Clause 6.3 link_

> _Standard text:_ Impact assessment — which controls / processes / risk-assessment scope is affected

<<GUIDANCE>>

### Chg Approval

<<MUST item:4.3:chg_approval>>
_Why: Clause 4.3 — determined_

> _Standard text:_ Approval signature with date (top management or delegated authority)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Chg Comms

<<SHOULD item:4.3:chg_comms>>
_Why: Operational discipline_

> _Standard text:_ Communication of the change to affected stakeholders

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
