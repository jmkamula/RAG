---
leaf_id: req:Art.26:joint_controller_register
control_ref: Art.26
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Joint Controller Register

> Per-relationship record for every active joint-controller arrangement. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.26:joint_controller_register -->
<!-- column: item:Art.26:reg_counterparty -->
<!-- column: item:Art.26:reg_activity -->
<!-- column: item:Art.26:reg_responsibilities -->
<!-- column: item:Art.26:reg_essence_published -->
<!-- column: item:Art.26:reg_signed_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.26:joint_controller_register -->
| Reg Counterparty | Reg Activity | Reg Responsibilities | Reg Essence Published | Reg Signed Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.26:joint_controller_register -->

## Column guidance — what to fill in

### Reg Counterparty

<<MUST item:Art.26:reg_counterparty>>
_Why: Audit_

> _Standard text:_ Per-row joint-controller counterparty

### Reg Activity

<<MUST item:Art.26:reg_activity>>
_Why: Cross-article_

> _Standard text:_ Per-row processing activity (Art.30 RoPA reference)

### Reg Responsibilities

<<MUST item:Art.26:reg_responsibilities>>
_Why: Art.26.1_

> _Standard text:_ Per-row responsibility split summary

### Reg Essence Published

<<MUST item:Art.26:reg_essence_published>>
_Why: Art.26.2_

> _Standard text:_ Per-row essence-of-arrangement published location (privacy notice URL)

### Reg Signed Date

<<MUST item:Art.26:reg_signed_date>>
_Why: Currency_

> _Standard text:_ Per-row arrangement signature date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Review Date

<<SHOULD item:Art.26:reg_review_date>>
_Why: Planning_

> _Standard text:_ Per-row next-review date
