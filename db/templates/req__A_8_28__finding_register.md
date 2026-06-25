---
leaf_id: req:A.8.28:finding_register
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Secure Coding Finding Register

> Per-finding tracking — SAST / SCA / review findings, severity, remediation SLA

<!-- TABLE-COLUMNS leaf:req:A.8.28:finding_register -->
<!-- column: item:A.8.28:reg_finding_id -->
<!-- column: item:A.8.28:reg_source -->
<!-- column: item:A.8.28:reg_severity -->
<!-- column: item:A.8.28:reg_sla_due -->
<!-- column: item:A.8.28:reg_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.28:finding_register -->
| Reg Finding Id | Reg Source | Reg Severity | Reg Sla Due | Reg Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.28:finding_register -->

## Column guidance — what to fill in

### Reg Finding Id

<<MUST item:A.8.28:reg_finding_id>>
_Why: Auditability_

> _Standard text:_ Per-finding unique identifier

### Reg Source

<<MUST item:A.8.28:reg_source>>
_Why: Identification_

> _Standard text:_ Per-finding source (SAST / SCA / manual review / external researcher)

### Reg Severity

<<MUST item:A.8.28:reg_severity>>
_Why: 27002:8.28 — applied_

> _Standard text:_ Per-finding severity

### Reg Sla Due

<<MUST item:A.8.28:reg_sla_due>>
_Why: Cross-control coherence_

> _Standard text:_ Per-finding SLA due date (matches A.8.8 vulnerability rubric for runtime-exploitable; relaxed for dev-time-only)

### Reg Status

<<MUST item:A.8.28:reg_status>>
_Why: Continuous evidence_

> _Standard text:_ Per-finding status (open / fixed / accepted-with-expiry)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Pattern Signal

<<SHOULD item:A.8.28:reg_pattern_signal>>
_Why: Continuous improvement_

> _Standard text:_ Per-finding pattern flag (repeating patterns flagged for training feedback)
