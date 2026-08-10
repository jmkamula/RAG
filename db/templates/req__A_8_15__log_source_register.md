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

<<DOC_CONTROL>>

> Per-source register — what's emitting logs, where they land, what retention applies, last-event timestamp (drives 'silent source' detection)

<!-- TABLE-COLUMNS leaf:req:A.8.15:log_source_register -->
<!-- column: item:A.8.15:reg_source_id -->
<!-- column: item:A.8.15:reg_log_class -->
<!-- column: item:A.8.15:reg_destination -->
<!-- column: item:A.8.15:reg_retention_tier -->
<!-- column: item:A.8.15:reg_last_event -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all your log sources, where their logs are stored, how long they're kept, and when they last sent data. It's useful for spotting inactive sources and meeting compliance requirements.

## When to use it

Use this register at all times to maintain an up-to-date overview of your log sources. Update it whenever you add, change, or retire a log source, or as your environment evolves.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per log source to fill in the required details from scratch. The total time depends on how many log sources you have.

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

<<GUIDANCE>>

### Reg Log Class

<<MUST item:A.8.15:reg_log_class>>
_Why: 27002:8.15 — record_

> _Standard text:_ Per-source log class (auth / access / change / fault / business-event / privacy-relevant)

<<GUIDANCE>>

### Reg Destination

<<MUST item:A.8.15:reg_destination>>
_Why: 27002:8.15 — stored_

> _Standard text:_ Per-source collection destination (SIEM index / cold-archive bucket / regulator-required path)

<<GUIDANCE>>

### Reg Retention Tier

<<MUST item:A.8.15:reg_retention_tier>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-source retention tier applied

<<GUIDANCE>>

### Reg Last Event

<<MUST item:A.8.15:reg_last_event>>
_Why: Drift detection_

> _Standard text:_ Per-source last-event timestamp (drives silent-source detection — common detection gap)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.15:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-source named owner (system / app owner)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
