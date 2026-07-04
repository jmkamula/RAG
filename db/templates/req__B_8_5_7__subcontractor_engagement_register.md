---
leaf_id: req:B.8.5.7:subcontractor_engagement_register
control_ref: B.8.5.7
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Subcontractor Engagement Register

> Per-subcontractor row — the audit trail of authorisation + contract + Annex B coverage. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.7:subcontractor_engagement_register -->
<!-- column: item:B.8.5.7:reg_subcontractor_id -->
<!-- column: item:B.8.5.7:reg_customer_authorisation -->
<!-- column: item:B.8.5.7:reg_contract_reference -->
<!-- column: item:B.8.5.7:reg_annex_b_coverage -->
<!-- column: item:B.8.5.7:reg_engagement_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.7:subcontractor_engagement_register -->
| Reg Subcontractor Id | Reg Customer Authorisation | Reg Contract Reference | Reg Annex B Coverage | Reg Engagement Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.7:subcontractor_engagement_register -->

## Column guidance — what to fill in

### Reg Subcontractor Id

<<MUST item:B.8.5.7:reg_subcontractor_id>>
_Why: Referenceability_

> _Standard text:_ Subcontractor identifier per row

### Reg Customer Authorisation

<<MUST item:B.8.5.7:reg_customer_authorisation>>
_Why: §8.5.7 — customer contract_

> _Standard text:_ Customer authorisation reference per row (general or specific)

### Reg Contract Reference

<<MUST item:B.8.5.7:reg_contract_reference>>
_Why: §8.5.7 — written contract_

> _Standard text:_ Executed contract reference per row

### Reg Annex B Coverage

<<MUST item:B.8.5.7:reg_annex_b_coverage>>
_Why: §8.5.7 — Annex B_

> _Standard text:_ Annex B controls covered per row (all / itemised)

### Reg Engagement Date

<<MUST item:B.8.5.7:reg_engagement_date>>
_Why: Currency_

> _Standard text:_ Engagement effective date per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Processing Scope

<<SHOULD item:B.8.5.7:reg_processing_scope>>
_Why: Traceability_

> _Standard text:_ Processing scope per row (what the subcontractor does)
