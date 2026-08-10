---
leaf_id: req:A.7.3.3:notice_delivery_log
control_ref: A.7.3.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Notice Delivery Log

<<DOC_CONTROL>>

> Per-delivery-touchpoint row — where + when the notice is surfaced (signup form / cookie banner / in-product prompt / periodic reminder). Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.3:notice_delivery_log -->
<!-- column: item:A.7.3.3:reg_touchpoint_id -->
<!-- column: item:A.7.3.3:reg_touchpoint_type -->
<!-- column: item:A.7.3.3:reg_notice_version -->
<!-- column: item:A.7.3.3:reg_deployment_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every time and place you show privacy notices to users, making it easier to demonstrate compliance with privacy standards like ISO 27701.

## When to use it

Use this log whenever your process or system matches specific privacy triggers, and plan to review and update it about once a year to keep information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each delivery instance; if you have several touchpoints, filling out the register from scratch may take 1-2 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.3:notice_delivery_log -->
| Reg Touchpoint Id | Reg Touchpoint Type | Reg Notice Version | Reg Deployment Date |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.3:notice_delivery_log -->

## Column guidance — what to fill in

### Reg Touchpoint Id

<<MUST item:A.7.3.3:reg_touchpoint_id>>
_Why: Referenceability_

> _Standard text:_ Unique touchpoint identifier per row

<<GUIDANCE>>

### Reg Touchpoint Type

<<MUST item:A.7.3.3:reg_touchpoint_type>>
_Why: §7.3.3 — at time of collection_

> _Standard text:_ Touchpoint type per row (signup / renewal / cookie banner / just-in-time prompt / periodic reminder)

<<GUIDANCE>>

### Reg Notice Version

<<MUST item:A.7.3.3:reg_notice_version>>
_Why: Traceability_

> _Standard text:_ Notice version served per row (link to A.7.3.2 artifact register)

<<GUIDANCE>>

### Reg Deployment Date

<<MUST item:A.7.3.3:reg_deployment_date>>
_Why: Currency_

> _Standard text:_ Deployment date per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Engagement Metric

<<SHOULD item:A.7.3.3:reg_engagement_metric>>
_Why: Effectiveness signal_

> _Standard text:_ Engagement metric per row (view count, expand-detail rate)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
