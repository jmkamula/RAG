---
leaf_id: req:Art.14:source_register
control_ref: Art.14
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.14 Source Register

<<DOC_CONTROL>>

> Per-source record — every third-party source from which personal data is obtained, with notice-delivery evidence. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.14:source_register -->
<!-- column: item:Art.14:reg_source_id -->
<!-- column: item:Art.14:reg_category -->
<!-- column: item:Art.14:reg_lawful_basis -->
<!-- column: item:Art.14:reg_notice_method -->
<!-- column: item:Art.14:reg_notice_deadline -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every third-party source from which you collect personal data, along with proof that you’ve provided the required privacy notice.

## When to use it

Use this register whenever you obtain personal data from external sources, and update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10–15 minutes per required element for each source you list, so the total time depends on how many third-party sources you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.14:source_register -->
| Reg Source Id | Reg Category | Reg Lawful Basis | Reg Notice Method | Reg Notice Deadline |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.14:source_register -->

## Column guidance — what to fill in

### Reg Source Id

<<MUST item:Art.14:reg_source_id>>
_Why: Audit defensibility_

> _Standard text:_ Source identifier per row (data broker name, public source URL, affiliate)

<<GUIDANCE>>

### Reg Category

<<MUST item:Art.14:reg_category>>
_Why: Coverage_

> _Standard text:_ Categories obtained per row (matches Art.14.1d notice item)

<<GUIDANCE>>

### Reg Lawful Basis

<<MUST item:Art.14:reg_lawful_basis>>
_Why: Cross-article coherence_

> _Standard text:_ Lawful basis per row (Art.6 entry id)

<<GUIDANCE>>

### Reg Notice Method

<<MUST item:Art.14:reg_notice_method>>
_Why: Art.14.3_

> _Standard text:_ Notice delivery method per row (email, in-app on first communication, etc.)

<<GUIDANCE>>

### Reg Notice Deadline

<<MUST item:Art.14:reg_notice_deadline>>
_Why: Art.14.3_

> _Standard text:_ Notice deadline met per row (within 1 month / first communication / first disclosure)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Exception

<<SHOULD item:Art.14:reg_exception>>
_Why: Art.14.5_

> _Standard text:_ Per-row Art.14.5 exception cited where notice is not provided (proportionate-impossibility / disclosure-by-law / confidentiality)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
