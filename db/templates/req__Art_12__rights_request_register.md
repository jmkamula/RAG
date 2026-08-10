---
leaf_id: req:Art.12:rights_request_register
control_ref: Art.12
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Rights Request Register

<<DOC_CONTROL>>

> Per-request record covering EVERY data subject right exercise (Art.15-22). Centralised log — drives Art.12.3 SLA tracking. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.12:rights_request_register -->
<!-- column: item:Art.12:reg_request_id -->
<!-- column: item:Art.12:reg_right_type -->
<!-- column: item:Art.12:reg_request_date -->
<!-- column: item:Art.12:reg_response_date -->
<!-- column: item:Art.12:reg_outcome -->
<!-- column: item:Art.12:reg_sla_met -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, central record of every request individuals make about their personal data rights under GDPR. It supports tracking and managing your response deadlines efficiently.

## When to use it

Use this register whenever someone exercises their data rights, such as access or deletion requests. Review and update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch typically takes about 1 to 1.5 hours for the initial required details, plus extra time for each new request you log throughout the year.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.12:rights_request_register -->
| Reg Request Id | Reg Right Type | Reg Request Date | Reg Response Date | Reg Outcome | Reg Sla Met |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.12:rights_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.12:reg_request_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique request identifier per row

<<GUIDANCE>>

### Reg Right Type

<<MUST item:Art.12:reg_right_type>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row right type (Art.15 access / Art.16 rectification / Art.17 erasure / Art.18 restriction / Art.20 portability / Art.21 objection / Art.22 automated)

<<GUIDANCE>>

### Reg Request Date

<<MUST item:Art.12:reg_request_date>>
_Why: SLA tracking_

> _Standard text:_ Per-row request received date

<<GUIDANCE>>

### Reg Response Date

<<MUST item:Art.12:reg_response_date>>
_Why: Art.12.3 SLA_

> _Standard text:_ Per-row response sent date (or extension notice date)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:Art.12:reg_outcome>>
_Why: Audit clarity_

> _Standard text:_ Per-row outcome (fulfilled / partial / refused with grounds / extended)

<<GUIDANCE>>

### Reg Sla Met

<<MUST item:Art.12:reg_sla_met>>
_Why: Art.12.3 — timeliness_

> _Standard text:_ Per-row SLA-met flag (one month or notified extension)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Identity Method

<<SHOULD item:Art.12:reg_identity_method>>
_Why: Art.12.6 audit_

> _Standard text:_ Per-row identity verification method used

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
