---
leaf_id: req:A.5.9:asset_reconciliation_review
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Periodic Asset Inventory Reconciliation

> Periodic reconciliation of the register against discovery feeds. The cadence is quarterly (freshness=90) because asset drift is daily and the register's value collapses fast without reconciliation. Annual review is insufficient for this control. Outputs feed back into the register and into procurement / cloud-provisioning hooks

<!-- TABLE-COLUMNS leaf:req:A.5.9:asset_reconciliation_review -->
<!-- column: item:A.5.9:rev_date -->
<!-- column: item:A.5.9:rev_reviewer -->
<!-- column: item:A.5.9:rev_per_source -->
<!-- column: item:A.5.9:rev_unassigned_owner -->
<!-- column: item:A.5.9:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.9:asset_reconciliation_review -->
| Rev Date | Rev Reviewer | Rev Per Source | Rev Unassigned Owner | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.9:asset_reconciliation_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.9:rev_date>>
_Why: 27002:5.9 — maintained_

> _Standard text:_ Reconciliation date within the planned interval (typically within 90 days of last reconciliation)

### Rev Reviewer

<<MUST item:A.5.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded

### Rev Per Source

<<MUST item:A.5.9:rev_per_source>>
_Why: 27002:5.9 — develop and maintain_

> _Standard text:_ Per-source delta — what each discovery source surfaced vs what the register held (additions, removals, mismatches)

### Rev Unassigned Owner

<<MUST item:A.5.9:rev_unassigned_owner>>
_Why: 27002:5.9d_

> _Standard text:_ Treatment of unassigned-owner rows (owner assignment forced or row retired)

### Rev Register Update

<<MUST item:A.5.9:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Register updated as a result of the reconciliation with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Classification Check

<<SHOULD item:A.5.9:rev_classification_check>>
_Why: A.5.12 / drift catch_

> _Standard text:_ Classification sampling check — are A.5.12 classifications still appropriate for the asset's actual use

### Rev Next Date

<<SHOULD item:A.5.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned reconciliation date stated
