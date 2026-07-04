---
leaf_id: req:A.7.2.6:processor_contract_register
control_ref: A.7.2.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# PII Processor Contract Register

> Per-processor row — the register of PII processors engaged, the executed contract, its scope + expiry + Annex B coverage. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.6:processor_contract_register -->
<!-- column: item:A.7.2.6:reg_processor_id -->
<!-- column: item:A.7.2.6:reg_contract_reference -->
<!-- column: item:A.7.2.6:reg_service_scope -->
<!-- column: item:A.7.2.6:reg_annex_b_coverage -->
<!-- column: item:A.7.2.6:reg_subprocessor_flag -->
<!-- column: item:A.7.2.6:reg_expiry -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.6:processor_contract_register -->
| Reg Processor Id | Reg Contract Reference | Reg Service Scope | Reg Annex B Coverage | Reg Subprocessor Flag | Reg Expiry |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.6:processor_contract_register -->

## Column guidance — what to fill in

### Reg Processor Id

<<MUST item:A.7.2.6:reg_processor_id>>
_Why: Referenceability_

> _Standard text:_ Processor identifier per row (legal entity name)

### Reg Contract Reference

<<MUST item:A.7.2.6:reg_contract_reference>>
_Why: §7.2.6 — written contract_

> _Standard text:_ Executed contract reference (document + version + signature date)

### Reg Service Scope

<<MUST item:A.7.2.6:reg_service_scope>>
_Why: Art.28.3 subject matter + nature_

> _Standard text:_ Service scope per row (what the processor does + PII categories involved)

### Reg Annex B Coverage

<<MUST item:A.7.2.6:reg_annex_b_coverage>>
_Why: §7.2.6 — all controls in Annex B assumed relevant_

> _Standard text:_ Annex B controls covered per row (either 'all' or itemised subset with justification link)

### Reg Subprocessor Flag

<<MUST item:A.7.2.6:reg_subprocessor_flag>>
_Why: Art.28.2_

> _Standard text:_ Subprocessors permitted flag + list per row

### Reg Expiry

<<MUST item:A.7.2.6:reg_expiry>>
_Why: Currency_

> _Standard text:_ Contract expiry / renewal date per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Audit

<<SHOULD item:A.7.2.6:reg_last_audit>>
_Why: Cross-link A.5.22 supplier review_

> _Standard text:_ Last processor audit / due-diligence date per row
