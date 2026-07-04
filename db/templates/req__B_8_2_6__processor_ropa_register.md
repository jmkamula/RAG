---
leaf_id: req:B.8.2.6:processor_ropa_register
control_ref: B.8.2.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Processor Records of Processing (RoPA)

> §8.2.6 requires processor-side records of processing carried out on behalf of each customer. Per-customer processing record. Register-as-primary (records_program spine). Bridges to Art.30.2 — smaller field set than controller RoPA (Art.30.1) but same secure-maintenance discipline.

<!-- TABLE-COLUMNS leaf:req:B.8.2.6:processor_ropa_register -->
<!-- column: item:B.8.2.6:ropa_customer_id -->
<!-- column: item:B.8.2.6:ropa_processing_categories -->
<!-- column: item:B.8.2.6:ropa_transfers -->
<!-- column: item:B.8.2.6:ropa_security_measures -->
<!-- column: item:B.8.2.6:ropa_subprocessor_list -->
<!-- column: item:B.8.2.6:ropa_processor_dpo -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.6:processor_ropa_register -->
| Ropa Customer Id | Ropa Processing Categories | Ropa Transfers | Ropa Security Measures | Ropa Subprocessor List | Ropa Processor Dpo |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.6:processor_ropa_register -->

## Column guidance — what to fill in

### Ropa Customer Id

<<MUST item:B.8.2.6:ropa_customer_id>>
_Why: Referenceability_

> _Standard text:_ Customer identifier per row (each controller the org processes for)

### Ropa Processing Categories

<<MUST item:B.8.2.6:ropa_processing_categories>>
_Why: §8.2.6 — categories of processing carried out_

> _Standard text:_ Categories of processing carried out per customer per row (Art.30.2.b)

### Ropa Transfers

<<MUST item:B.8.2.6:ropa_transfers>>
_Why: §8.2.6 — transfers to third countries_

> _Standard text:_ Third-country / international-org transfers per row (Art.30.2.c) with cited safeguards

### Ropa Security Measures

<<MUST item:B.8.2.6:ropa_security_measures>>
_Why: §8.2.6 — technical and organizational security measures_

> _Standard text:_ General description of technical + organizational measures per row (Art.30.2.d)

### Ropa Subprocessor List

<<MUST item:B.8.2.6:ropa_subprocessor_list>>
_Why: Coverage_

> _Standard text:_ Subprocessor list per row (Art.30.2 + Art.28.2)

### Ropa Processor Dpo

<<MUST item:B.8.2.6:ropa_processor_dpo>>
_Why: Art.30.2.a_

> _Standard text:_ Processor DPO / representative contact if applicable (Art.30.2.a)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Ropa Last Verified

<<SHOULD item:B.8.2.6:ropa_last_verified>>
_Why: Currency_

> _Standard text:_ Last verification date per row (against customer instruction record)
