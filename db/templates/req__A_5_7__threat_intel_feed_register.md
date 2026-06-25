---
leaf_id: req:A.5.7:threat_intel_feed_register
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Threat Intelligence Feed Register

> A.5.7 requires a curated set of sources, not an ad-hoc list. The feed register catalogues every active intelligence source with metadata that allows the program review to assess which feeds deliver value: source name, layer, owner inside the org, last received signal, cost, signal/noise rating. Decommissioned feeds are retained with end-date for traceability

<!-- TABLE-COLUMNS leaf:req:A.5.7:threat_intel_feed_register -->
<!-- column: item:A.5.7:reg_source_id -->
<!-- column: item:A.5.7:reg_layer -->
<!-- column: item:A.5.7:reg_owner -->
<!-- column: item:A.5.7:reg_last_received -->
<!-- column: item:A.5.7:reg_cost -->
<!-- column: item:A.5.7:reg_signal_rating -->
<!-- column: item:A.5.7:reg_internal_input -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.7:threat_intel_feed_register -->
| Reg Source Id | Reg Layer | Reg Owner | Reg Last Received | Reg Cost | Reg Signal Rating | Reg Internal Input |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.7:threat_intel_feed_register -->

## Column guidance — what to fill in

### Reg Source Id

<<MUST item:A.5.7:reg_source_id>>
_Why: 27002:5.7 — sources_

> _Standard text:_ Each active source captured with a unique identifier

### Reg Layer

<<MUST item:A.5.7:reg_layer>>
_Why: 27002:5.7 — three layers_

> _Standard text:_ Intelligence layer per row (strategic / tactical / operational)

### Reg Owner

<<MUST item:A.5.7:reg_owner>>
_Why: Accountability_

> _Standard text:_ Internal owner per row accountable for the source (renewal, escalation, value assessment)

### Reg Last Received

<<MUST item:A.5.7:reg_last_received>>
_Why: 27002:5.7 — collection cadence verified_

> _Standard text:_ Last-received timestamp per row (stale-feed detection)

### Reg Cost

<<MUST item:A.5.7:reg_cost>>
_Why: Program economics_

> _Standard text:_ Cost per row (paid feeds vs free) — required for value review

### Reg Signal Rating

<<MUST item:A.5.7:reg_signal_rating>>
_Why: 27002:5.7 — relevance_

> _Standard text:_ Signal/noise rating per row (high/medium/low) updated at each program review

### Reg Internal Input

<<MUST item:A.5.7:reg_internal_input>>
_Why: 27002:5.7 — internal/external balance_

> _Standard text:_ Internal sources captured alongside external (e.g. A.5.6 SIG-membership outputs, internal IR observations)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Decommissioned

<<SHOULD item:A.5.7:reg_decommissioned>>
_Why: Operational discipline_

> _Standard text:_ Decommissioned sources retained with end-date and reason (audit trail)

### Reg Contact

<<SHOULD item:A.5.7:reg_contact>>
_Why: Operational continuity_

> _Standard text:_ Contact per row (vendor support, ISAC liaison)
