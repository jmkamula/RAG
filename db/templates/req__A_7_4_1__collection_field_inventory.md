---
leaf_id: req:A.7.4.1:collection_field_inventory
control_ref: A.7.4.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Collection Field Inventory

<<DOC_CONTROL>>

> Per-field row — every PII field the org collects (direct + indirect) with necessity rationale + default state (opt-in vs required). Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.1:collection_field_inventory -->
<!-- column: item:A.7.4.1:reg_field_id -->
<!-- column: item:A.7.4.1:reg_purpose_link -->
<!-- column: item:A.7.4.1:reg_necessity_rationale -->
<!-- column: item:A.7.4.1:reg_default_state -->
<!-- column: item:A.7.4.1:reg_collection_mode -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every piece of personal information your organization collects, along with why you need it and whether it’s optional or required.

## When to use it

Use this template when your organization handles personal data and needs to track each field collected, especially if your privacy profile matches certain requirements. Plan to update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10 to 15 minutes per field you document, so the total time will depend on how many types of personal information you collect.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.1:collection_field_inventory -->
| Reg Field Id | Reg Purpose Link | Reg Necessity Rationale | Reg Default State | Reg Collection Mode |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.1:collection_field_inventory -->

## Column guidance — what to fill in

### Reg Field Id

<<MUST item:A.7.4.1:reg_field_id>>
_Why: Referenceability_

> _Standard text:_ Unique field identifier per row (form_id + field_name)

<<GUIDANCE>>

### Reg Purpose Link

<<MUST item:A.7.4.1:reg_purpose_link>>
_Why: §7.4.1 — for identified purposes_

> _Standard text:_ Purpose link per row (which A.7.2.1 purpose this field supports)

<<GUIDANCE>>

### Reg Necessity Rationale

<<MUST item:A.7.4.1:reg_necessity_rationale>>
_Why: §7.4.1 — adequate, relevant, necessary_

> _Standard text:_ Necessity rationale per row (adequate / relevant / necessary explanation)

<<GUIDANCE>>

### Reg Default State

<<MUST item:A.7.4.1:reg_default_state>>
_Why: §7.4.1 — disabled by default_

> _Standard text:_ Default state per row (required / opt-in optional / opt-out optional)

<<GUIDANCE>>

### Reg Collection Mode

<<MUST item:A.7.4.1:reg_collection_mode>>
_Why: §7.4.1 — indirect collection_

> _Standard text:_ Collection mode per row (direct form / cookie / weblog / API integration / third-party enrichment)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Reviewed

<<SHOULD item:A.7.4.1:reg_last_reviewed>>
_Why: Currency_

> _Standard text:_ Last necessity-review date per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
