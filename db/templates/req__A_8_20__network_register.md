---
leaf_id: req:A.8.20:network_register
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Network Inventory Register

> Per-network inventory — segment id, classification, perimeter type, owner. Drives 'every segment has a documented zone + perimeter' audit

<!-- TABLE-COLUMNS leaf:req:A.8.20:network_register -->
<!-- column: item:A.8.20:reg_segment_id -->
<!-- column: item:A.8.20:reg_classification -->
<!-- column: item:A.8.20:reg_zone -->
<!-- column: item:A.8.20:reg_perimeter -->
<!-- column: item:A.8.20:reg_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.20:network_register -->
| Reg Segment Id | Reg Classification | Reg Zone | Reg Perimeter | Reg Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.20:network_register -->

## Column guidance — what to fill in

### Reg Segment Id

<<MUST item:A.8.20:reg_segment_id>>
_Why: Identification_

> _Standard text:_ Per-row segment / VPC / VLAN identifier

### Reg Classification

<<MUST item:A.8.20:reg_classification>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row classification tier (from A.5.12)

### Reg Zone

<<MUST item:A.8.20:reg_zone>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row zone assignment (matches A.8.22 zone model)

### Reg Perimeter

<<MUST item:A.8.20:reg_perimeter>>
_Why: 27002:8.20 — perimeter_

> _Standard text:_ Per-row perimeter type (boundary firewall / service mesh / IAP / vendor-managed)

### Reg Owner

<<MUST item:A.8.20:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row named owner (network engineer accountable)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Audited

<<SHOULD item:A.8.20:reg_last_audited>>
_Why: Drift detection_

> _Standard text:_ Per-row last-audited timestamp (drives drift detection)
