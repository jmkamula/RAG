---
leaf_id: req:A.7.3.8:copy_request_register
control_ref: A.7.3.8
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Copy Request Register

> Per-request row — audit trail of copy requests with format used, scope covered, and SLA. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.8:copy_request_register -->
<!-- column: item:A.7.3.8:reg_request_id -->
<!-- column: item:A.7.3.8:reg_subject_id -->
<!-- column: item:A.7.3.8:reg_format_delivered -->
<!-- column: item:A.7.3.8:reg_scope_summary -->
<!-- column: item:A.7.3.8:reg_response_time -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.8:copy_request_register -->
| Reg Request Id | Reg Subject Id | Reg Format Delivered | Reg Scope Summary | Reg Response Time |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.8:copy_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:A.7.3.8:reg_request_id>>
_Why: Audit trail_

> _Standard text:_ Unique request identifier per row

### Reg Subject Id

<<MUST item:A.7.3.8:reg_subject_id>>
_Why: Traceability_

> _Standard text:_ Subject identifier per row

### Reg Format Delivered

<<MUST item:A.7.3.8:reg_format_delivered>>
_Why: §7.3.8 — structured format_

> _Standard text:_ Format delivered per row (JSON / CSV / PDF / structured export)

### Reg Scope Summary

<<MUST item:A.7.3.8:reg_scope_summary>>
_Why: §7.3.8 — relate specifically_

> _Standard text:_ Scope summary per row (what PII was included)

### Reg Response Time

<<MUST item:A.7.3.8:reg_response_time>>
_Why: Art.12.3_

> _Standard text:_ Response time per row (vs SLA)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Direct Transfer

<<SHOULD item:A.7.3.8:reg_direct_transfer>>
_Why: Art.20.2_

> _Standard text:_ Direct-transfer flag if Art.20.2 invoked
