---
leaf_id: req:A.7.2.2:lawful_basis_register
control_ref: A.7.2.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Lawful Basis Register

<<DOC_CONTROL>>

> Per-activity lawful basis record — the documented basis for every processing activity. Annual refresh (freshness=365).

## What this template gives you

This template helps you keep a clear, organized record of the legal reasons for each way you use personal data in your business. It supports privacy compliance and makes audits or reviews much easier.

## When to use it

Use this register when your organization needs to document the lawful basis for every data processing activity, especially if your privacy profile or regulations require it. Plan to update it about once a year to stay current.

## Prerequisites
<<PREREQUISITES>>

<!-- TABLE-COLUMNS leaf:req:A.7.2.2:lawful_basis_register -->
<!-- column: item:A.7.2.2:reg_activity_id -->
<!-- column: item:A.7.2.2:reg_primary_basis -->
<!-- column: item:A.7.2.2:reg_special_category_basis -->
<!-- column: item:A.7.2.2:reg_lia_reference -->
<!-- column: item:A.7.2.2:reg_purpose_link -->
<!-- /TABLE-COLUMNS -->

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each processing activity you record. Completing the register from scratch typically takes 1-2 hours, depending on how many activities you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.2:lawful_basis_register -->
| Reg Activity Id | Reg Primary Basis | Reg Special Category Basis | Reg Lia Reference | Reg Purpose Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.2:lawful_basis_register -->

## Column guidance — what to fill in

### Reg Activity Id

<<MUST item:A.7.2.2:reg_activity_id>>
_Why: Traceability_

> _Standard text:_ Processing activity identifier per row

<<GUIDANCE>>

### Reg Primary Basis

<<MUST item:A.7.2.2:reg_primary_basis>>
_Why: §7.2.2 — documented_

> _Standard text:_ Primary basis cited per row (Art.6.1.a-f or equivalent)

<<GUIDANCE>>

### Reg Special Category Basis

<<MUST item:A.7.2.2:reg_special_category_basis>>
_Why: GDPR Art.9.2_

> _Standard text:_ Special-category basis where applicable (Art.9.2.a-j / Art.10 basis)

<<GUIDANCE>>

### Reg Lia Reference

<<MUST item:A.7.2.2:reg_lia_reference>>
_Why: Art.6.1.f — balancing test recorded_

> _Standard text:_ LIA reference per row where basis is legitimate interests

<<GUIDANCE>>

### Reg Purpose Link

<<MUST item:A.7.2.2:reg_purpose_link>>
_Why: §7.2.1 cross-link_

> _Standard text:_ Purpose link (which A.7.2.1 purpose(s) this basis authorises)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Basis Date

<<SHOULD item:A.7.2.2:reg_basis_date>>
_Why: Currency_

> _Standard text:_ Date basis established / last re-evaluated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
