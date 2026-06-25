---
leaf_id: req:Art.21:objection_register
control_ref: Art.21
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Objection Register

> Per-objection record. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.21:objection_register -->
<!-- column: item:Art.21:reg_request_id -->
<!-- column: item:Art.21:reg_objection_type -->
<!-- column: item:Art.21:reg_outcome -->
<!-- column: item:Art.21:reg_grounds -->
<!-- column: item:Art.21:reg_response_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.21:objection_register -->
| Reg Request Id | Reg Objection Type | Reg Outcome | Reg Grounds | Reg Response Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.21:objection_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.21:reg_request_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row request id (Art.12 cross-ref)

### Reg Objection Type

<<MUST item:Art.21:reg_objection_type>>
_Why: Art.21.1-6_

> _Standard text:_ Per-row objection type (direct marketing absolute / legitimate interests balancing / scientific research)

### Reg Outcome

<<MUST item:Art.21:reg_outcome>>
_Why: Art.21.1_

> _Standard text:_ Per-row outcome (processing ceased / continued with compelling grounds / partial)

### Reg Grounds

<<MUST item:Art.21:reg_grounds>>
_Why: Art.21.1 — defensibility_

> _Standard text:_ Per-row grounds for continuing (for legitimate-interests objections continued)

### Reg Response Date

<<MUST item:Art.21:reg_response_date>>
_Why: Art.12.3_

> _Standard text:_ Per-row response date (Art.12.3 SLA tracking)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Suppression List

<<SHOULD item:Art.21:reg_suppression_list>>
_Why: Art.21.3 operational_

> _Standard text:_ Per-row addition to suppression list (direct marketing)
