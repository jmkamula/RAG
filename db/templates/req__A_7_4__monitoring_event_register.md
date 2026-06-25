---
leaf_id: req:A.7.4:monitoring_event_register
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Monitoring Event Register

> The catalogue of detection events worth investigating — anomalous access attempts, alarms triggered, CCTV-detected behaviour requiring review. Subset of raw detection signal (after first-pass filtering)

<!-- TABLE-COLUMNS leaf:req:A.7.4:monitoring_event_register -->
<!-- column: item:A.7.4:reg_event_id -->
<!-- column: item:A.7.4:reg_source -->
<!-- column: item:A.7.4:reg_timestamp -->
<!-- column: item:A.7.4:reg_classification -->
<!-- column: item:A.7.4:reg_outcome -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4:monitoring_event_register -->
| Reg Event Id | Reg Source | Reg Timestamp | Reg Classification | Reg Outcome |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4:monitoring_event_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.4:reg_event_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-event unique identifier

### Reg Source

<<MUST item:A.7.4:reg_source>>
_Why: 27002:7.4 — detection_

> _Standard text:_ Per-event source (CCTV / IDS / access-control / alarm)

### Reg Timestamp

<<MUST item:A.7.4:reg_timestamp>>
_Why: Operational discipline_

> _Standard text:_ Per-event timestamp

### Reg Classification

<<MUST item:A.7.4:reg_classification>>
_Why: 27002:7.4 — alert response_

> _Standard text:_ Per-event classification (true-positive / false-positive / requires-investigation)

### Reg Outcome

<<MUST item:A.7.4:reg_outcome>>
_Why: Closes the loop_

> _Standard text:_ Per-event outcome (closed-no-action / handed-to-A.5.26-incident / lessons-captured)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Evidence Link

<<SHOULD item:A.7.4:reg_evidence_link>>
_Why: Cross-control coherence_

> _Standard text:_ Per-event evidence-package link (CCTV clip reference, log excerpt — for cases handed to A.5.28 evidence handling)
