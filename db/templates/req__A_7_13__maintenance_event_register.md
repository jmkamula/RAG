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

> The catalogue of maintenance events — equipment id, date, provider, supervision, outcome, post-verification

<!-- TABLE-COLUMNS leaf:req:A.7.13:maintenance_event_register -->
<!-- column: item:A.7.13:reg_event_id -->
<!-- column: item:A.7.13:reg_equipment -->
<!-- column: item:A.7.13:reg_date -->
<!-- column: item:A.7.13:reg_provider -->
<!-- column: item:A.7.13:reg_supervision_outcome -->
<!-- column: item:A.7.13:reg_post_verify -->
<!-- /TABLE-COLUMNS -->

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

### Reg Equipment

<<MUST item:A.7.13:reg_equipment>>
_Why: Cross-control coherence_

> _Standard text:_ Per-event equipment (cross-link to A.5.9 asset register)

### Reg Date

<<MUST item:A.7.13:reg_date>>
_Why: Operational discipline_

> _Standard text:_ Per-event date

### Reg Provider

<<MUST item:A.7.13:reg_provider>>
_Why: 27002:7.13 — authorised_

> _Standard text:_ Per-event provider (from authorised list)

### Reg Supervision Outcome

<<MUST item:A.7.13:reg_supervision_outcome>>
_Why: 27002:7.13 — confidentiality_

> _Standard text:_ Per-event supervision outcome (in-house supervised / unsupervised-with-justification / pre-cleared provider)

### Reg Post Verify

<<MUST item:A.7.13:reg_post_verify>>
_Why: 27002:7.13 — integrity_

> _Standard text:_ Per-event post-verification result (passed / failed-with-action)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Offsite Chain

<<SHOULD item:A.7.13:reg_offsite_chain>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-event offsite-maintenance chain-of-custody where applicable
