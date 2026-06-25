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

> Per-change record capturing each scope amendment — the lifecycle-end artefact that proves scope changes are deliberate and approved, not silent drift

<!-- TABLE-COLUMNS leaf:req:4.3:scope_change_record -->
<!-- column: item:4.3:chg_trigger -->
<!-- column: item:4.3:chg_summary -->
<!-- column: item:4.3:chg_impact -->
<!-- column: item:4.3:chg_approval -->
<!-- /TABLE-COLUMNS -->

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

### Chg Summary

<<MUST item:4.3:chg_summary>>
_Why: Audit clarity_

> _Standard text:_ Change summary — what was added or removed from scope

### Chg Impact

<<MUST item:4.3:chg_impact>>
_Why: Clause 6.3 link_

> _Standard text:_ Impact assessment — which controls / processes / risk-assessment scope is affected

### Chg Approval

<<MUST item:4.3:chg_approval>>
_Why: Clause 4.3 — determined_

> _Standard text:_ Approval signature with date (top management or delegated authority)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Chg Comms

<<SHOULD item:4.3:chg_comms>>
_Why: Operational discipline_

> _Standard text:_ Communication of the change to affected stakeholders
