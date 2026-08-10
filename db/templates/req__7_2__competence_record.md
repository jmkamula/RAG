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

<<DOC_CONTROL>>

> Clause 7.2 requires the organisation to determine necessary competence of persons whose work affects ISMS performance and ensure they are competent. The record is the canonical artefact mapping role → required competence → actual competence → gap actions. Sibling leaves: determination procedure, applicable roles scope, program review. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.2:competence_record -->
<!-- column: item:7.2:required_competence -->
<!-- column: item:7.2:basis_of_competence -->
<!-- column: item:7.2:effectiveness -->
<!-- column: item:7.2:documented -->
<!-- column: item:7.2:owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track and document the skills and qualifications needed for each role that impacts your information security management system, making it easier to identify and address any gaps.

## When to use it

Use this register whenever you need to show that your team members are qualified for their roles under ISO 27001, and plan to review and update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element, plus additional time for each role you include. Completing it from scratch typically takes 1-2 hours, depending on your team size.

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

<<GUIDANCE>>

### Basis Of Competence

<<MUST item:7.2:basis_of_competence>>
_Why: Clause 7.2 b)_

> _Standard text:_ Basis of competence (education, training, experience) recorded per person

<<GUIDANCE>>

### Effectiveness

<<MUST item:7.2:effectiveness>>
_Why: Clause 7.2 c)_

> _Standard text:_ Evaluation that competence actions were effective

<<GUIDANCE>>

### Documented

<<MUST item:7.2:documented>>
_Why: Clause 7.2 d)_

> _Standard text:_ Documented information retained as evidence of competence

<<GUIDANCE>>

### Owner

<<MUST item:7.2:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the record (HR partner with ISMS Manager)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Training Matrix

<<SHOULD item:7.2:training_matrix>>
_Why: Operational view_

> _Standard text:_ Training matrix per role (current + required)

<<GUIDANCE>>

### Gap Actions

<<SHOULD item:7.2:gap_actions>>
_Why: Clause 7.2 c) — conditional_

> _Standard text:_ Actions taken to close competence gaps (training, hiring, mentoring) where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
