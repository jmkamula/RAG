---
leaf_id: req:B.8.2.2:purpose_adherence_register
control_ref: B.8.2.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Customer Purpose Adherence Register

> Per-customer row — the stated purposes + technical-binding controls + any side-processing carve-outs. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.2.2:purpose_adherence_register -->
<!-- column: item:B.8.2.2:reg_customer_id -->
<!-- column: item:B.8.2.2:reg_stated_purposes -->
<!-- column: item:B.8.2.2:reg_binding_controls -->
<!-- column: item:B.8.2.2:reg_permitted_secondary -->
<!-- column: item:B.8.2.2:reg_last_verified -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.2:purpose_adherence_register -->
| Reg Customer Id | Reg Stated Purposes | Reg Binding Controls | Reg Permitted Secondary | Reg Last Verified |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.2:purpose_adherence_register -->

## Column guidance — what to fill in

### Reg Customer Id

<<MUST item:B.8.2.2:reg_customer_id>>
_Why: Traceability_

> _Standard text:_ Customer identifier per row

### Reg Stated Purposes

<<MUST item:B.8.2.2:reg_stated_purposes>>
_Why: §8.2.2 — documented instructions_

> _Standard text:_ Stated customer purposes per row (from B.8.2.1 agreement)

### Reg Binding Controls

<<MUST item:B.8.2.2:reg_binding_controls>>
_Why: §8.2.2 — only processed for purposes_

> _Standard text:_ Binding controls per row (tenant isolation config / data-tag enforcement / access scoping)

### Reg Permitted Secondary

<<MUST item:B.8.2.2:reg_permitted_secondary>>
_Why: §8.2.2 — express instruction_

> _Standard text:_ Permitted secondary uses per row (where customer has authorised anonymised aggregate use)

### Reg Last Verified

<<MUST item:B.8.2.2:reg_last_verified>>
_Why: Currency_

> _Standard text:_ Last verification date per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Audit History

<<SHOULD item:B.8.2.2:reg_customer_audit_history>>
_Why: §8.2.2 — allow verification_

> _Standard text:_ Customer audit history — recent customer audits + findings
