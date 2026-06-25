---
leaf_id: req:7.2:competence_record
control_ref: 7.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# ISMS Competence Record

> Clause 7.2 requires the organisation to determine necessary competence of persons whose work affects ISMS performance and ensure they are competent. The record is the canonical artefact mapping role → required competence → actual competence → gap actions. Sibling leaves: determination procedure, applicable roles scope, program review. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.2:competence_record -->
<!-- column: item:7.2:required_competence -->
<!-- column: item:7.2:basis_of_competence -->
<!-- column: item:7.2:effectiveness -->
<!-- column: item:7.2:documented -->
<!-- column: item:7.2:owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.2:competence_record -->
| Required Competence | Basis Of Competence | Effectiveness | Documented | Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.2:competence_record -->

## Column guidance — what to fill in

### Required Competence

<<MUST item:7.2:required_competence>>
_Why: Clause 7.2 a)_

> _Standard text:_ Required competence defined per role affecting ISMS performance

### Basis Of Competence

<<MUST item:7.2:basis_of_competence>>
_Why: Clause 7.2 b)_

> _Standard text:_ Basis of competence (education, training, experience) recorded per person

### Effectiveness

<<MUST item:7.2:effectiveness>>
_Why: Clause 7.2 c)_

> _Standard text:_ Evaluation that competence actions were effective

### Documented

<<MUST item:7.2:documented>>
_Why: Clause 7.2 d)_

> _Standard text:_ Documented information retained as evidence of competence

### Owner

<<MUST item:7.2:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the record (HR partner with ISMS Manager)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Training Matrix

<<SHOULD item:7.2:training_matrix>>
_Why: Operational view_

> _Standard text:_ Training matrix per role (current + required)

### Gap Actions

<<SHOULD item:7.2:gap_actions>>
_Why: Clause 7.2 c) — conditional_

> _Standard text:_ Actions taken to close competence gaps (training, hiring, mentoring) where applicable
