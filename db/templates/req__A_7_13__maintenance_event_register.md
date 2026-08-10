---
leaf_id: req:A.7.13:maintenance_event_register
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Maintenance Event Register

<<DOC_CONTROL>>

> The catalogue of maintenance events — equipment id, date, provider, supervision, outcome, post-verification

<!-- TABLE-COLUMNS leaf:req:A.7.13:maintenance_event_register -->
<!-- column: item:A.7.13:reg_event_id -->
<!-- column: item:A.7.13:reg_equipment -->
<!-- column: item:A.7.13:reg_date -->
<!-- column: item:A.7.13:reg_provider -->
<!-- column: item:A.7.13:reg_supervision_outcome -->
<!-- column: item:A.7.13:reg_post_verify -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all maintenance activities for your equipment, including key details like dates, providers, and outcomes. It’s useful for tracking compliance and ensuring maintenance is properly documented.

## When to use it

Use this register whenever maintenance occurs in your environment, and update it as needed to reflect new events or changes. It’s designed to be kept current at all times.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the initial register, plus 10 to 15 minutes for each new maintenance event you add.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.13:maintenance_event_register -->
| Reg Event Id | Reg Equipment | Reg Date | Reg Provider | Reg Supervision Outcome | Reg Post Verify |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.13:maintenance_event_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.13:reg_event_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-event unique identifier

<<GUIDANCE>>

### Reg Equipment

<<MUST item:A.7.13:reg_equipment>>
_Why: Cross-control coherence_

> _Standard text:_ Per-event equipment (cross-link to A.5.9 asset register)

<<GUIDANCE>>

### Reg Date

<<MUST item:A.7.13:reg_date>>
_Why: Operational discipline_

> _Standard text:_ Per-event date

<<GUIDANCE>>

### Reg Provider

<<MUST item:A.7.13:reg_provider>>
_Why: 27002:7.13 — authorised_

> _Standard text:_ Per-event provider (from authorised list)

<<GUIDANCE>>

### Reg Supervision Outcome

<<MUST item:A.7.13:reg_supervision_outcome>>
_Why: 27002:7.13 — confidentiality_

> _Standard text:_ Per-event supervision outcome (in-house supervised / unsupervised-with-justification / pre-cleared provider)

<<GUIDANCE>>

### Reg Post Verify

<<MUST item:A.7.13:reg_post_verify>>
_Why: 27002:7.13 — integrity_

> _Standard text:_ Per-event post-verification result (passed / failed-with-action)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Offsite Chain

<<SHOULD item:A.7.13:reg_offsite_chain>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-event offsite-maintenance chain-of-custody where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
