---
leaf_id: req:A.8.15:log_source_register
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Log Source Register

> Per-source register — what's emitting logs, where they land, what retention applies, last-event timestamp (drives 'silent source' detection)

<!-- TABLE-COLUMNS leaf:req:A.8.15:log_source_register -->
<!-- column: item:A.8.15:reg_source_id -->
<!-- column: item:A.8.15:reg_log_class -->
<!-- column: item:A.8.15:reg_destination -->
<!-- column: item:A.8.15:reg_retention_tier -->
<!-- column: item:A.8.15:reg_last_event -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.15:log_source_register -->
| Reg Source Id | Reg Log Class | Reg Destination | Reg Retention Tier | Reg Last Event |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.15:log_source_register -->

## Column guidance — what to fill in

### Reg Source Id

<<MUST item:A.8.15:reg_source_id>>
_Why: Identification_

> _Standard text:_ Per-source identifier (system / app / network device)

### Reg Log Class

<<MUST item:A.8.15:reg_log_class>>
_Why: 27002:8.15 — record_

> _Standard text:_ Per-source log class (auth / access / change / fault / business-event / privacy-relevant)

### Reg Destination

<<MUST item:A.8.15:reg_destination>>
_Why: 27002:8.15 — stored_

> _Standard text:_ Per-source collection destination (SIEM index / cold-archive bucket / regulator-required path)

### Reg Retention Tier

<<MUST item:A.8.15:reg_retention_tier>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-source retention tier applied

### Reg Last Event

<<MUST item:A.8.15:reg_last_event>>
_Why: Drift detection_

> _Standard text:_ Per-source last-event timestamp (drives silent-source detection — common detection gap)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.15:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-source named owner (system / app owner)
