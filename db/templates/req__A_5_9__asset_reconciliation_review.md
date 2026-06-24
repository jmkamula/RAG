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
---

# Periodic Asset Inventory Reconciliation

> Periodic reconciliation of the register against discovery feeds. The cadence is quarterly (freshness=90) because asset drift is daily and the register's value collapses fast without reconciliation. Annual review is insufficient for this control. Outputs feed back into the register and into procurement / cloud-provisioning hooks

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Reconciliation date within the planned interval (typically within 90 days of last reconciliation)

<<MUST item:A.5.9:rev_date>>
_Why: 27002:5.9 — maintained_

<<TEXT>>

## 2. Reviewer identity and role recorded

<<MUST item:A.5.9:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-source delta — what each discovery source surfaced vs what the register held (additions, removals, mismatches)

<<MUST item:A.5.9:rev_per_source>>
_Why: 27002:5.9 — develop and maintain_

<<TEXT>>

## 4. Treatment of unassigned-owner rows (owner assignment forced or row retired)

<<MUST item:A.5.9:rev_unassigned_owner>>
_Why: 27002:5.9d_

<<TEXT>>

## 5. Register updated as a result of the reconciliation with reference to this review

<<MUST item:A.5.9:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Classification sampling check — are A.5.12 classifications still appropriate for the asset's actual use

<<SHOULD item:A.5.9:rev_classification_check>>
_Why: A.5.12 / drift catch_

<<TEXT>>

### 2. Next planned reconciliation date stated

<<SHOULD item:A.5.9:rev_next_date>>
_Why: Planning_

<<TEXT>>
