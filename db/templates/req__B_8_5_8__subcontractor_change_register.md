---
leaf_id: req:B.8.5.8:subcontractor_change_register
control_ref: B.8.5.8
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Subcontractor Change Register

<<DOC_CONTROL>>

> Per-change-event row — every subcontractor add / replace with customer notification date + objection status. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.8:subcontractor_change_register -->
<!-- column: item:B.8.5.8:reg_change_id -->
<!-- column: item:B.8.5.8:reg_change_type -->
<!-- column: item:B.8.5.8:reg_notification_date -->
<!-- column: item:B.8.5.8:reg_effective_date -->
<!-- column: item:B.8.5.8:reg_objection_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date record of every time you add or replace a subcontractor, including when you notified your customer and whether they raised any objections.

## When to use it

Use this register whenever you change your subcontractors and need to track customer notifications and responses. Plan to review and update it about once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each change event. Completing the register from scratch may take around an hour, depending on the number of subcontractor changes you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.8:subcontractor_change_register -->
| Reg Change Id | Reg Change Type | Reg Notification Date | Reg Effective Date | Reg Objection Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.8:subcontractor_change_register -->

## Column guidance — what to fill in

### Reg Change Id

<<MUST item:B.8.5.8:reg_change_id>>
_Why: Audit trail_

> _Standard text:_ Unique change identifier per row

<<GUIDANCE>>

### Reg Change Type

<<MUST item:B.8.5.8:reg_change_type>>
_Why: §8.5.8_

> _Standard text:_ Change type per row (add / replace / remove)

<<GUIDANCE>>

### Reg Notification Date

<<MUST item:B.8.5.8:reg_notification_date>>
_Why: §8.5.8 — inform customer_

> _Standard text:_ Customer notification date per row

<<GUIDANCE>>

### Reg Effective Date

<<MUST item:B.8.5.8:reg_effective_date>>
_Why: Traceability_

> _Standard text:_ Change effective date per row

<<GUIDANCE>>

### Reg Objection Status

<<MUST item:B.8.5.8:reg_objection_status>>
_Why: §8.5.8 — opportunity to object_

> _Standard text:_ Objection status per row (none / raised / resolved / termination)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Resolution

<<SHOULD item:B.8.5.8:reg_resolution>>
_Why: Audit trail_

> _Standard text:_ Resolution per row where objection raised

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
