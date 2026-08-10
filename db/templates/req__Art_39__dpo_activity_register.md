---
leaf_id: req:Art.39:dpo_activity_register
control_ref: Art.39
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Activity Register

<<DOC_CONTROL>>

> Per-period activity log proving DPO is performing the Art.39 tasks. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.39:dpo_activity_register -->
<!-- column: item:Art.39:reg_period -->
<!-- column: item:Art.39:reg_advice_log -->
<!-- column: item:Art.39:reg_monitoring_activities -->
<!-- column: item:Art.39:reg_dpia_engagements -->
<!-- column: item:Art.39:reg_sa_interactions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record showing your Data Protection Officer is carrying out their required GDPR tasks. It’s useful for demonstrating compliance during audits or regulatory reviews.

## When to use it

Use this register if your organization is required to appoint a Data Protection Officer and needs to track their activities under GDPR Article 39. Update it about once a year, or whenever your circumstances change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours to complete the required sections for the first time, depending on how much activity you need to record. Additional entries will take less time as you update it annually.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.39:dpo_activity_register -->
| Reg Period | Reg Advice Log | Reg Monitoring Activities | Reg Dpia Engagements | Reg Sa Interactions |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.39:dpo_activity_register -->

## Column guidance — what to fill in

### Reg Period

<<MUST item:Art.39:reg_period>>
_Why: Cadence_

> _Standard text:_ Per-row reporting period

<<GUIDANCE>>

### Reg Advice Log

<<MUST item:Art.39:reg_advice_log>>
_Why: Art.39.1.a_

> _Standard text:_ Per-row advice given log (informal queries + formal opinions)

<<GUIDANCE>>

### Reg Monitoring Activities

<<MUST item:Art.39:reg_monitoring_activities>>
_Why: Art.39.1.b_

> _Standard text:_ Per-row monitoring activities (audits, sample reviews, compliance checks)

<<GUIDANCE>>

### Reg Dpia Engagements

<<MUST item:Art.39:reg_dpia_engagements>>
_Why: Art.39.1.c_

> _Standard text:_ Per-row DPIA engagements (which DPIAs DPO advised on)

<<GUIDANCE>>

### Reg Sa Interactions

<<MUST item:Art.39:reg_sa_interactions>>
_Why: Art.39.1.d-e_

> _Standard text:_ Per-row SA interactions (consultations, inquiries handled)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Training Delivered

<<SHOULD item:Art.39:reg_training_delivered>>
_Why: Art.39.1.b_

> _Standard text:_ Per-row training / awareness sessions delivered

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
