---
leaf_id: req:B.8.5.6:subcontractor_disclosure_register
control_ref: B.8.5.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Subcontractor Disclosure Register

<<DOC_CONTROL>>

> Per-subcontractor-per-customer row — the audit trail of subcontractor disclosures. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.6:subcontractor_disclosure_register -->
<!-- column: item:B.8.5.6:reg_subcontractor_id -->
<!-- column: item:B.8.5.6:reg_customer_id -->
<!-- column: item:B.8.5.6:reg_disclosure_date -->
<!-- column: item:B.8.5.6:reg_countries -->
<!-- column: item:B.8.5.6:reg_disclosure_mode -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all subcontractor disclosures for each customer, making it easier to demonstrate compliance with privacy standards like ISO 27701.

## When to use it

Use this register whenever you work with subcontractors and need to track disclosures for each customer, updating it about once a year or whenever your business profile changes in ways that require new disclosures.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10–15 minutes per required element for each subcontractor-customer entry; setting up the register from scratch may take an hour or more, depending on the number of relationships you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.6:subcontractor_disclosure_register -->
| Reg Subcontractor Id | Reg Customer Id | Reg Disclosure Date | Reg Countries | Reg Disclosure Mode |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.6:subcontractor_disclosure_register -->

## Column guidance — what to fill in

### Reg Subcontractor Id

<<MUST item:B.8.5.6:reg_subcontractor_id>>
_Why: Referenceability_

> _Standard text:_ Subcontractor identifier per row

<<GUIDANCE>>

### Reg Customer Id

<<MUST item:B.8.5.6:reg_customer_id>>
_Why: Traceability_

> _Standard text:_ Customer per row

<<GUIDANCE>>

### Reg Disclosure Date

<<MUST item:B.8.5.6:reg_disclosure_date>>
_Why: §8.5.6 — before use_

> _Standard text:_ Disclosure date per row (pre-use)

<<GUIDANCE>>

### Reg Countries

<<MUST item:B.8.5.6:reg_countries>>
_Why: §8.5.6 — countries_

> _Standard text:_ Countries + international orgs disclosed per row

<<GUIDANCE>>

### Reg Disclosure Mode

<<MUST item:B.8.5.6:reg_disclosure_mode>>
_Why: §8.5.6_

> _Standard text:_ Disclosure mode per row (public trust page / DPA schedule / NDA + on-request)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Ack

<<SHOULD item:B.8.5.6:reg_customer_ack>>
_Why: Confirmation_

> _Standard text:_ Customer acknowledgement per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
