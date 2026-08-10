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

<<DOC_CONTROL>>

> Per-processor row — the register of PII processors engaged, the executed contract, its scope + expiry + Annex B coverage. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.6:processor_contract_register -->
<!-- column: item:A.7.2.6:reg_processor_id -->
<!-- column: item:A.7.2.6:reg_contract_reference -->
<!-- column: item:A.7.2.6:reg_service_scope -->
<!-- column: item:A.7.2.6:reg_annex_b_coverage -->
<!-- column: item:A.7.2.6:reg_subprocessor_flag -->
<!-- column: item:A.7.2.6:reg_expiry -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all third parties processing personal data for your organization, including details about their contracts, scope, and compliance with privacy requirements.

## When to use it

Use this register whenever you engage a new service provider to process personal data, and update it at least once a year to ensure all contract details and coverage remain current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each processor you add, so the total time depends on how many processors you work with; for a single entry, plan for about 1-2 hours.

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

<<GUIDANCE>>

### Reg Contract Reference

<<MUST item:A.7.2.6:reg_contract_reference>>
_Why: §7.2.6 — written contract_

> _Standard text:_ Executed contract reference (document + version + signature date)

<<GUIDANCE>>

### Reg Service Scope

<<MUST item:A.7.2.6:reg_service_scope>>
_Why: Art.28.3 subject matter + nature_

> _Standard text:_ Service scope per row (what the processor does + PII categories involved)

<<GUIDANCE>>

### Reg Annex B Coverage

<<MUST item:A.7.2.6:reg_annex_b_coverage>>
_Why: §7.2.6 — all controls in Annex B assumed relevant_

> _Standard text:_ Annex B controls covered per row (either 'all' or itemised subset with justification link)

<<GUIDANCE>>

### Reg Subprocessor Flag

<<MUST item:A.7.2.6:reg_subprocessor_flag>>
_Why: Art.28.2_

> _Standard text:_ Subprocessors permitted flag + list per row

<<GUIDANCE>>

### Reg Expiry

<<MUST item:A.7.2.6:reg_expiry>>
_Why: Currency_

> _Standard text:_ Contract expiry / renewal date per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Audit

<<SHOULD item:A.7.2.6:reg_last_audit>>
_Why: Cross-link A.5.22 supplier review_

> _Standard text:_ Last processor audit / due-diligence date per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
