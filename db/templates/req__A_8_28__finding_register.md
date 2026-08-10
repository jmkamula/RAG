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

<<DOC_CONTROL>>

> Per-finding tracking — SAST / SCA / review findings, severity, remediation SLA

<!-- TABLE-COLUMNS leaf:req:A.8.28:finding_register -->
<!-- column: item:A.8.28:reg_finding_id -->
<!-- column: item:A.8.28:reg_source -->
<!-- column: item:A.8.28:reg_severity -->
<!-- column: item:A.8.28:reg_sla_due -->
<!-- column: item:A.8.28:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of secure coding issues found during code scans or reviews, including their severity and how quickly they need to be fixed. It provides a clear, organized way to manage and monitor remediation progress.

## When to use it

Use this register whenever your organization identifies secure coding findings through automated tools or manual reviews. Update it as new findings arise or existing ones are resolved, keeping it current as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes setting up the initial required elements, plus additional time for each finding you add. The effort will increase as more findings are tracked.

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

<<GUIDANCE>>

### Reg Source

<<MUST item:A.8.28:reg_source>>
_Why: Identification_

> _Standard text:_ Per-finding source (SAST / SCA / manual review / external researcher)

<<GUIDANCE>>

### Reg Severity

<<MUST item:A.8.28:reg_severity>>
_Why: 27002:8.28 — applied_

> _Standard text:_ Per-finding severity

<<GUIDANCE>>

### Reg Sla Due

<<MUST item:A.8.28:reg_sla_due>>
_Why: Cross-control coherence_

> _Standard text:_ Per-finding SLA due date (matches A.8.8 vulnerability rubric for runtime-exploitable; relaxed for dev-time-only)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.8.28:reg_status>>
_Why: Continuous evidence_

> _Standard text:_ Per-finding status (open / fixed / accepted-with-expiry)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Pattern Signal

<<SHOULD item:A.8.28:reg_pattern_signal>>
_Why: Continuous improvement_

> _Standard text:_ Per-finding pattern flag (repeating patterns flagged for training feedback)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
