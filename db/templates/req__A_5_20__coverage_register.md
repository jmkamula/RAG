---
leaf_id: req:A.5.20:coverage_register
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Supplier Agreement Coverage Register

<<DOC_CONTROL>>

> An approved template alone does not protect the org — each supplier agreement must actually carry the relevant clauses. The coverage register tracks, per supplier, the template version applied, the date the agreement was signed, the agreement term, and the supplier tier — so it is auditable that the agreed clauses are in force

<!-- TABLE-COLUMNS leaf:req:A.5.20:coverage_register -->
<!-- column: item:A.5.20:cov_template_version -->
<!-- column: item:A.5.20:cov_signed_date -->
<!-- column: item:A.5.20:cov_term -->
<!-- column: item:A.5.20:cov_tier -->
<!-- column: item:A.5.20:cov_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of which supplier agreements use the correct contract clauses, making it easy to show auditors that your agreements are up to date and compliant.

## When to use it

Use this register whenever you sign or update a supplier agreement, and review it whenever there are changes to your suppliers or contract templates.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each supplier, so setting up the register from scratch may take an hour or more, depending on how many suppliers you have.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.20:coverage_register -->
| Cov Template Version | Cov Signed Date | Cov Term | Cov Tier | Cov Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.20:coverage_register -->

## Column guidance — what to fill in

### Cov Template Version

<<MUST item:A.5.20:cov_template_version>>
_Why: 27002:5.20 — agreed_

> _Standard text:_ Template version applied per supplier

<<GUIDANCE>>

### Cov Signed Date

<<MUST item:A.5.20:cov_signed_date>>
_Why: Accountability_

> _Standard text:_ Signed-date of the active agreement per supplier

<<GUIDANCE>>

### Cov Term

<<MUST item:A.5.20:cov_term>>
_Why: Lifecycle_

> _Standard text:_ Agreement term and renewal/expiry date per row

<<GUIDANCE>>

### Cov Tier

<<MUST item:A.5.20:cov_tier>>
_Why: Proportionality_

> _Standard text:_ Supplier tier per row (drives which clause variant is required)

<<GUIDANCE>>

### Cov Owner

<<MUST item:A.5.20:cov_owner>>
_Why: Accountability_

> _Standard text:_ Named owner accountable for the agreement (typically procurement or legal partner)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Cov Subprocessors

<<SHOULD item:A.5.20:cov_subprocessors>>
_Why: 27002:5.20j_

> _Standard text:_ Approved sub-processors per supplier tracked (link to A.5.19 supplier register)

<<GUIDANCE>>

### Cov Jurisdiction

<<SHOULD item:A.5.20:cov_jurisdiction>>
_Why: 27002:5.20c,p_

> _Standard text:_ Governing jurisdiction per agreement

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
