---
leaf_id: req:Art.48:foreign_request_register
control_ref: Art.48
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Foreign Authority Request Register

> Per-request record (most orgs will have empty register — that's a defensible outcome). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.48:foreign_request_register -->
<!-- column: item:Art.48:reg_request_id -->
<!-- column: item:Art.48:reg_authority -->
<!-- column: item:Art.48:reg_legal_basis_check -->
<!-- column: item:Art.48:reg_decision -->
<!-- column: item:Art.48:reg_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.48:foreign_request_register -->
| Reg Request Id | Reg Authority | Reg Legal Basis Check | Reg Decision | Reg Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.48:foreign_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.48:reg_request_id>>
_Why: Audit_

> _Standard text:_ Per-row request id (or 'no requests this period' affirmative statement)

### Reg Authority

<<MUST item:Art.48:reg_authority>>
_Why: Defensibility_

> _Standard text:_ Per-row requesting authority + jurisdiction

### Reg Legal Basis Check

<<MUST item:Art.48:reg_legal_basis_check>>
_Why: Art.48_

> _Standard text:_ Per-row legal-basis check outcome (international agreement / Art.49 derogation / refused)

### Reg Decision

<<MUST item:Art.48:reg_decision>>
_Why: Audit clarity_

> _Standard text:_ Per-row decision (disclosed / partially-disclosed / refused)

### Reg Date

<<MUST item:Art.48:reg_date>>
_Why: Currency_

> _Standard text:_ Per-row decision date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:Art.48:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Per-row legal counsel review evidence
