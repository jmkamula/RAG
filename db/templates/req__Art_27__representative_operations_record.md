---
leaf_id: req:Art.27:representative_operations_record
control_ref: Art.27
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Representative Operations Record

<<DOC_CONTROL>>

> Per-interaction record of how the representative actually operates — handled queries from SAs and subjects, escalated to non-EU principal. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.27:representative_operations_record -->
<!-- column: item:Art.27:reg_interaction_id -->
<!-- column: item:Art.27:reg_originator -->
<!-- column: item:Art.27:reg_topic -->
<!-- column: item:Art.27:reg_escalation -->
<!-- column: item:Art.27:reg_resolution_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of how your representative handles queries and escalations, making it easier to demonstrate compliance with GDPR requirements.

## When to use it

Use this template if your organization needs to document representative activities under GDPR Article 27, especially when your profile involves handling queries from supervisory authorities or data subjects. Update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours filling this out from scratch, depending on the number of required details and the amount of activity to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.27:representative_operations_record -->
| Reg Interaction Id | Reg Originator | Reg Topic | Reg Escalation | Reg Resolution Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.27:representative_operations_record -->

## Column guidance — what to fill in

### Reg Interaction Id

<<MUST item:Art.27:reg_interaction_id>>
_Why: Audit_

> _Standard text:_ Per-row interaction id

<<GUIDANCE>>

### Reg Originator

<<MUST item:Art.27:reg_originator>>
_Why: Art.27.4_

> _Standard text:_ Per-row originator (data subject / SA / other)

<<GUIDANCE>>

### Reg Topic

<<MUST item:Art.27:reg_topic>>
_Why: Art.27.4_

> _Standard text:_ Per-row topic (rights request routing, SA inquiry, breach communication)

<<GUIDANCE>>

### Reg Escalation

<<MUST item:Art.27:reg_escalation>>
_Why: Defensibility_

> _Standard text:_ Per-row escalation to non-EU principal documented

<<GUIDANCE>>

### Reg Resolution Date

<<MUST item:Art.27:reg_resolution_date>>
_Why: SLA tracking_

> _Standard text:_ Per-row resolution date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Sla Met

<<SHOULD item:Art.27:reg_sla_met>>
_Why: Art.12 cross-link_

> _Standard text:_ Per-row SLA-met flag (response within Art.12.3 cascade)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
