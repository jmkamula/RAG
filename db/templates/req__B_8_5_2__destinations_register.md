---
leaf_id: req:B.8.5.2:destinations_register
control_ref: B.8.5.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Processor Transfer Destinations Register

<<DOC_CONTROL>>

> Per-destination row — countries + international orgs where customer PII may be processed. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.2:destinations_register -->
<!-- column: item:B.8.5.2:reg_destination_id -->
<!-- column: item:B.8.5.2:reg_role -->
<!-- column: item:B.8.5.2:reg_customer_disclosure -->
<!-- column: item:B.8.5.2:reg_basis_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all the countries and international organizations where your customers’ personal data may be processed. It’s designed to support privacy compliance and transparency for your data handling practices.

## When to use it

Use this register if your organization processes customer personal data in multiple countries or through international organizations. Update it about once a year, or whenever your data transfer destinations change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each destination you need to list. Completing the register from scratch may take 1-2 hours, depending on the number of destinations involved.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.2:destinations_register -->
| Reg Destination Id | Reg Role | Reg Customer Disclosure | Reg Basis Link |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.2:destinations_register -->

## Column guidance — what to fill in

### Reg Destination Id

<<MUST item:B.8.5.2:reg_destination_id>>
_Why: Referenceability_

> _Standard text:_ Destination identifier per row

<<GUIDANCE>>

### Reg Role

<<MUST item:B.8.5.2:reg_role>>
_Why: Traceability_

> _Standard text:_ Role per row (direct storage / subprocessor / support access)

<<GUIDANCE>>

### Reg Customer Disclosure

<<MUST item:B.8.5.2:reg_customer_disclosure>>
_Why: §8.5.2 — available to customers_

> _Standard text:_ Customer disclosure status per row (published in DPA schedule / trust page / on request)

<<GUIDANCE>>

### Reg Basis Link

<<MUST item:B.8.5.2:reg_basis_link>>
_Why: §8.5.2 — 8.5.1 alignment_

> _Standard text:_ Basis link per row (link to B.8.5.1)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Subprocessor Link

<<SHOULD item:B.8.5.2:reg_subprocessor_link>>
_Why: §8.5.2 — subcontracted_

> _Standard text:_ Subprocessor link per row where destination is via a subprocessor

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
