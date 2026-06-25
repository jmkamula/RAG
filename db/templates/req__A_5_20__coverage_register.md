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

> An approved template alone does not protect the org — each supplier agreement must actually carry the relevant clauses. The coverage register tracks, per supplier, the template version applied, the date the agreement was signed, the agreement term, and the supplier tier — so it is auditable that the agreed clauses are in force

<!-- TABLE-COLUMNS leaf:req:A.5.20:coverage_register -->
<!-- column: item:A.5.20:cov_template_version -->
<!-- column: item:A.5.20:cov_signed_date -->
<!-- column: item:A.5.20:cov_term -->
<!-- column: item:A.5.20:cov_tier -->
<!-- column: item:A.5.20:cov_owner -->
<!-- /TABLE-COLUMNS -->

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

### Cov Signed Date

<<MUST item:A.5.20:cov_signed_date>>
_Why: Accountability_

> _Standard text:_ Signed-date of the active agreement per supplier

### Cov Term

<<MUST item:A.5.20:cov_term>>
_Why: Lifecycle_

> _Standard text:_ Agreement term and renewal/expiry date per row

### Cov Tier

<<MUST item:A.5.20:cov_tier>>
_Why: Proportionality_

> _Standard text:_ Supplier tier per row (drives which clause variant is required)

### Cov Owner

<<MUST item:A.5.20:cov_owner>>
_Why: Accountability_

> _Standard text:_ Named owner accountable for the agreement (typically procurement or legal partner)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Cov Subprocessors

<<SHOULD item:A.5.20:cov_subprocessors>>
_Why: 27002:5.20j_

> _Standard text:_ Approved sub-processors per supplier tracked (link to A.5.19 supplier register)

### Cov Jurisdiction

<<SHOULD item:A.5.20:cov_jurisdiction>>
_Why: 27002:5.20c,p_

> _Standard text:_ Governing jurisdiction per agreement
