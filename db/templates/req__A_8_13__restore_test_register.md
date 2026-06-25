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

> Per-restore-test lifecycle-end record — what was restored, when, integrity-verified, target met. Parallels A.5.30 ICT readiness recovery-test pattern

<!-- TABLE-COLUMNS leaf:req:A.8.13:restore_test_register -->
<!-- column: item:A.8.13:reg_test_id -->
<!-- column: item:A.8.13:reg_target -->
<!-- column: item:A.8.13:reg_date -->
<!-- column: item:A.8.13:reg_outcome -->
<!-- column: item:A.8.13:reg_integrity_check -->
<!-- column: item:A.8.13:reg_rpo_met -->
<!-- /TABLE-COLUMNS -->

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

### Reg Target

<<MUST item:A.8.13:reg_target>>
_Why: 27002:8.13 — regularly tested_

> _Standard text:_ Per-test backup target tested (system / dataset / configuration)

### Reg Date

<<MUST item:A.8.13:reg_date>>
_Why: Currency_

> _Standard text:_ Per-test date

### Reg Outcome

<<MUST item:A.8.13:reg_outcome>>
_Why: 27002:8.13 — tested_

> _Standard text:_ Per-test outcome (success / partial / failure)

### Reg Integrity Check

<<MUST item:A.8.13:reg_integrity_check>>
_Why: Defensibility_

> _Standard text:_ Per-test integrity-verification artefact (checksum / hash / functional test of restored data)

### Reg Rpo Met

<<MUST item:A.8.13:reg_rpo_met>>
_Why: 27002:8.13 — sufficient_

> _Standard text:_ Per-test RPO-met flag (data-recoverable-to-RPO confirmed; auditor-critical proof parallels A.5.30 rec_success_status)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Findings

<<SHOULD item:A.8.13:reg_findings>>
_Why: Closes the loop_

> _Standard text:_ Per-test findings + corrective actions where target missed
