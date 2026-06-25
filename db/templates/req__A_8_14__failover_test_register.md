---
leaf_id: req:A.8.14:failover_test_register
control_ref: A.8.14
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Failover Test Register

> Per-test record — drilled failover events, real failover events, outcomes. Proves the baseline + procedure work in practice

<!-- TABLE-COLUMNS leaf:req:A.8.14:failover_test_register -->
<!-- column: item:A.8.14:reg_test_id -->
<!-- column: item:A.8.14:reg_service -->
<!-- column: item:A.8.14:reg_type -->
<!-- column: item:A.8.14:reg_date -->
<!-- column: item:A.8.14:reg_outcome -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.14:failover_test_register -->
| Reg Test Id | Reg Service | Reg Type | Reg Date | Reg Outcome |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.14:failover_test_register -->

## Column guidance — what to fill in

### Reg Test Id

<<MUST item:A.8.14:reg_test_id>>
_Why: Auditability_

> _Standard text:_ Per-test unique identifier

### Reg Service

<<MUST item:A.8.14:reg_service>>
_Why: 27002:8.14 — sufficient to meet_

> _Standard text:_ Per-test service tested

### Reg Type

<<MUST item:A.8.14:reg_type>>
_Why: Distinguishing operational vs test signal_

> _Standard text:_ Per-test type (planned drill / unplanned real / fault-injection)

### Reg Date

<<MUST item:A.8.14:reg_date>>
_Why: Currency_

> _Standard text:_ Per-test date

### Reg Outcome

<<MUST item:A.8.14:reg_outcome>>
_Why: 27002:8.14 — sufficient_

> _Standard text:_ Per-test outcome (success / partial / failure) + actual recovery time vs target

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Findings

<<SHOULD item:A.8.14:reg_findings>>
_Why: Closes the loop_

> _Standard text:_ Per-test findings + corrective actions where target missed
