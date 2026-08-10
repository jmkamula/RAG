---
leaf_id: req:A.7.2.1:purpose_register
control_ref: A.7.2.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# PII Processing Purpose Register

<<DOC_CONTROL>>

> Per-purpose row — the canonical list of every documented purpose the organisation processes PII for. Annual refresh (freshness=365). Feeds §7.3.2 notice and §7.2.8 RoPA.

<!-- TABLE-COLUMNS leaf:req:A.7.2.1:purpose_register -->
<!-- column: item:A.7.2.1:reg_purpose_id -->
<!-- column: item:A.7.2.1:reg_purpose_text -->
<!-- column: item:A.7.2.1:reg_activity_link -->
<!-- column: item:A.7.2.1:reg_categories -->
<!-- column: item:A.7.2.1:reg_lawful_basis_link -->
<!-- column: item:A.7.2.1:reg_retention -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly document every reason your organization processes personal information, making it easier to stay organized and meet privacy requirements.

## When to use it

Use this register when your organization processes personal data and needs to keep an up-to-date list of processing purposes. Plan to review and refresh it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each processing purpose you document. Completing the register from scratch may take a few hours, depending on how many purposes you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.1:purpose_register -->
| Reg Purpose Id | Reg Purpose Text | Reg Activity Link | Reg Categories | Reg Lawful Basis Link | Reg Retention |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.1:purpose_register -->

## Column guidance — what to fill in

### Reg Purpose Id

<<MUST item:A.7.2.1:reg_purpose_id>>
_Why: Referenceability_

> _Standard text:_ Unique purpose identifier per row

<<GUIDANCE>>

### Reg Purpose Text

<<MUST item:A.7.2.1:reg_purpose_text>>
_Why: §7.2.1 — specific purposes_

> _Standard text:_ Purpose statement text (clear + specific)

<<GUIDANCE>>

### Reg Activity Link

<<MUST item:A.7.2.1:reg_activity_link>>
_Why: §7.2.8 traceability_

> _Standard text:_ Processing activity link (which §7.2.8 RoPA row(s) implement this purpose)

<<GUIDANCE>>

### Reg Categories

<<MUST item:A.7.2.1:reg_categories>>
_Why: §7.2.1 implementation guidance_

> _Standard text:_ Categories of PII + categories of subjects per row

<<GUIDANCE>>

### Reg Lawful Basis Link

<<MUST item:A.7.2.1:reg_lawful_basis_link>>
_Why: §7.2.2 cross-link_

> _Standard text:_ Lawful basis link (which A.7.2.2 basis row this purpose relies on)

<<GUIDANCE>>

### Reg Retention

<<MUST item:A.7.2.1:reg_retention>>
_Why: Storage limitation_

> _Standard text:_ Retention period per purpose

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Notice Link

<<SHOULD item:A.7.2.1:reg_notice_link>>
_Why: §7.3.2 traceability_

> _Standard text:_ Notice link — which §7.3.2 notice text discloses this purpose to subjects

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
