---
leaf_id: req:Art.15:dsar_register
control_ref: Art.15
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# DSAR Register

> Living log of every access request received and its handling. Distinct from the per-event response leaf: the register is the universal record showing the population of requests, status, and timing compliance — auditor-facing evidence that the procedure operates in practice. Style v2 freshness 180d — high-volume DSAR data, slower than incident-register fast-data (90d) but faster than annual review

<!-- TABLE-COLUMNS leaf:req:Art.15:dsar_register -->
<!-- column: item:Art.15:reg_received_date -->
<!-- column: item:Art.15:reg_requester -->
<!-- column: item:Art.15:reg_scope -->
<!-- column: item:Art.15:reg_response_date -->
<!-- column: item:Art.15:reg_timing_flag -->
<!-- column: item:Art.15:reg_outcome -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.15:dsar_register -->
| Reg Received Date | Reg Requester | Reg Scope | Reg Response Date | Reg Timing Flag | Reg Outcome |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.15:dsar_register -->

## Column guidance — what to fill in

### Reg Received Date

<<MUST item:Art.15:reg_received_date>>
_Why: Art.12.3 timing_

> _Standard text:_ Request received date (the start of the Art.12.3 clock) per row

### Reg Requester

<<MUST item:Art.15:reg_requester>>
_Why: Art.12.6_

> _Standard text:_ Requester identity (verified) or pseudonymous reference where verification used a token

### Reg Scope

<<MUST item:Art.15:reg_scope>>
_Why: Operational clarity_

> _Standard text:_ Scope of the request as understood (full Art.15 / specific data set / repeat copy)

### Reg Response Date

<<MUST item:Art.15:reg_response_date>>
_Why: Art.12.3_

> _Standard text:_ Date the response was issued

### Reg Timing Flag

<<MUST item:Art.15:reg_timing_flag>>
_Why: Art.12.3_

> _Standard text:_ Timing compliance flag (within 1 month / extended per Art.12.3 / late)

### Reg Outcome

<<MUST item:Art.15:reg_outcome>>
_Why: Art.12.5 / Art.15.4_

> _Standard text:_ Outcome per row (fulfilled / partial under Art.15.4 / refused under Art.12.5 with reason)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Extension Reason

<<SHOULD item:Art.15:reg_extension_reason>>
_Why: Art.12.3_

> _Standard text:_ Extension reason captured when Art.12.3 two-month extension was used

### Reg Response Link

<<SHOULD item:Art.15:reg_response_link>>
_Why: Cross-leaf traceability_

> _Standard text:_ Linkage to the per-request response artifact (req:Art.15:dsar_response instance)
