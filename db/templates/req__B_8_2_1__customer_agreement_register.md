---
leaf_id: req:B.8.2.1:customer_agreement_register
control_ref: B.8.2.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Customer PII Agreement Register

> Per-customer row — the register of executed processing agreements, coverage of assistance obligations, term. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.2.1:customer_agreement_register -->
<!-- column: item:B.8.2.1:reg_customer_id -->
<!-- column: item:B.8.2.1:reg_agreement_reference -->
<!-- column: item:B.8.2.1:reg_assistance_coverage -->
<!-- column: item:B.8.2.1:reg_instructions_channel -->
<!-- column: item:B.8.2.1:reg_term -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.1:customer_agreement_register -->
| Reg Customer Id | Reg Agreement Reference | Reg Assistance Coverage | Reg Instructions Channel | Reg Term |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.1:customer_agreement_register -->

## Column guidance — what to fill in

### Reg Customer Id

<<MUST item:B.8.2.1:reg_customer_id>>
_Why: Referenceability_

> _Standard text:_ Customer identifier per row

### Reg Agreement Reference

<<MUST item:B.8.2.1:reg_agreement_reference>>
_Why: §8.2.1 — contract_

> _Standard text:_ Executed agreement document reference per row

### Reg Assistance Coverage

<<MUST item:B.8.2.1:reg_assistance_coverage>>
_Why: §8.2.1 — assistance obligations_

> _Standard text:_ Assistance coverage per row (which Art.28.3.e-h obligations addressed)

### Reg Instructions Channel

<<MUST item:B.8.2.1:reg_instructions_channel>>
_Why: Art.28.3.a_

> _Standard text:_ Documented-instructions channel per row (email log / ticket queue / portal)

### Reg Term

<<MUST item:B.8.2.1:reg_term>>
_Why: Currency_

> _Standard text:_ Term / expiry / renewal per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Role

<<SHOULD item:B.8.2.1:reg_customer_role>>
_Why: §8.2.1 — depending on customer's role_

> _Standard text:_ Customer role per row (controller / processor / joint) to route obligations correctly
