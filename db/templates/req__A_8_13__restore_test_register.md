---
leaf_id: req:A.8.13:restore_test_register
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Restore Test Register

<<DOC_CONTROL>>

> Per-restore-test lifecycle-end record — what was restored, when, integrity-verified, target met. Parallels A.5.30 ICT readiness recovery-test pattern

<!-- TABLE-COLUMNS leaf:req:A.8.13:restore_test_register -->
<!-- column: item:A.8.13:reg_test_id -->
<!-- column: item:A.8.13:reg_target -->
<!-- column: item:A.8.13:reg_date -->
<!-- column: item:A.8.13:reg_outcome -->
<!-- column: item:A.8.13:reg_integrity_check -->
<!-- column: item:A.8.13:reg_rpo_met -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of each restore test, including what was restored, when it happened, and whether the data was checked for integrity. It supports your compliance with ISO 27001 requirements for ICT recovery testing.

## When to use it

Use this register whenever you perform a restore test in your environment, and update it as needed to reflect new tests or changes. It should be maintained regularly to ensure accurate tracking.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes to complete all required sections for each restore test entry, depending on the amount of detail and number of tests you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.13:restore_test_register -->
| Reg Test Id | Reg Target | Reg Date | Reg Outcome | Reg Integrity Check | Reg Rpo Met |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.13:restore_test_register -->

## Column guidance — what to fill in

### Reg Test Id

<<MUST item:A.8.13:reg_test_id>>
_Why: Auditability_

> _Standard text:_ Per-test unique identifier

<<GUIDANCE>>

### Reg Target

<<MUST item:A.8.13:reg_target>>
_Why: 27002:8.13 — regularly tested_

> _Standard text:_ Per-test backup target tested (system / dataset / configuration)

<<GUIDANCE>>

### Reg Date

<<MUST item:A.8.13:reg_date>>
_Why: Currency_

> _Standard text:_ Per-test date

<<GUIDANCE>>

### Reg Outcome

<<MUST item:A.8.13:reg_outcome>>
_Why: 27002:8.13 — tested_

> _Standard text:_ Per-test outcome (success / partial / failure)

<<GUIDANCE>>

### Reg Integrity Check

<<MUST item:A.8.13:reg_integrity_check>>
_Why: Defensibility_

> _Standard text:_ Per-test integrity-verification artefact (checksum / hash / functional test of restored data)

<<GUIDANCE>>

### Reg Rpo Met

<<MUST item:A.8.13:reg_rpo_met>>
_Why: 27002:8.13 — sufficient_

> _Standard text:_ Per-test RPO-met flag (data-recoverable-to-RPO confirmed; auditor-critical proof parallels A.5.30 rec_success_status)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Findings

<<SHOULD item:A.8.13:reg_findings>>
_Why: Closes the loop_

> _Standard text:_ Per-test findings + corrective actions where target missed

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
