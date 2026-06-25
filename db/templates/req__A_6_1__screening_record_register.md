---
leaf_id: req:A.6.1:screening_record_register
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Per-Candidate Screening Record Register

> The operational catalogue of screening events. Every candidate / new hire / re-screened employee has a row: candidate identifier, role tier, checks performed, outcome, decision authority, decision date. Drives the audit-defensibility 'show me you screened this person before they got access' question

<!-- TABLE-COLUMNS leaf:req:A.6.1:screening_record_register -->
<!-- column: item:A.6.1:reg_candidate_id -->
<!-- column: item:A.6.1:reg_role_tier -->
<!-- column: item:A.6.1:reg_checks_performed -->
<!-- column: item:A.6.1:reg_outcome -->
<!-- column: item:A.6.1:reg_decision_date -->
<!-- column: item:A.6.1:reg_authoriser -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.1:screening_record_register -->
| Reg Candidate Id | Reg Role Tier | Reg Checks Performed | Reg Outcome | Reg Decision Date | Reg Authoriser |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.1:screening_record_register -->

## Column guidance — what to fill in

### Reg Candidate Id

<<MUST item:A.6.1:reg_candidate_id>>
_Why: Accountability_

> _Standard text:_ Per-record candidate identifier (links to identity register A.5.16 once hired; anonymised pre-hire to comply with data minimisation)

### Reg Role Tier

<<MUST item:A.6.1:reg_role_tier>>
_Why: 27002:6.1a — proportional_

> _Standard text:_ Role tier per record (drives the proportional check-depth applied; junior / standard / sensitive / privileged)

### Reg Checks Performed

<<MUST item:A.6.1:reg_checks_performed>>
_Why: 27002:6.1a — verification_

> _Standard text:_ Checks performed per record (identity / employment-history / education / criminal / financial / sanctions — actual checks run, not just planned)

### Reg Outcome

<<MUST item:A.6.1:reg_outcome>>
_Why: 27002:6.1 — decision_

> _Standard text:_ Outcome per record (cleared / cleared-with-conditions / blocked / superseded by waiver)

### Reg Decision Date

<<MUST item:A.6.1:reg_decision_date>>
_Why: Audit defensibility_

> _Standard text:_ Decision date per record (proves the screening completed BEFORE access was granted per A.5.18)

### Reg Authoriser

<<MUST item:A.6.1:reg_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser per record (named individual making the accept/reject decision)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Rescreen Date

<<SHOULD item:A.6.1:reg_rescreen_date>>
_Why: Operational discipline_

> _Standard text:_ Last rescreen date per record (for roles with ongoing-check obligations)

### Reg Provider Ref

<<SHOULD item:A.6.1:reg_provider_ref>>
_Why: Traceability_

> _Standard text:_ Third-party provider reference per record where used
