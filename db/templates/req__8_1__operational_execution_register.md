---
leaf_id: req:8.1:operational_execution_register
control_ref: 8.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Operational Execution Register

> Per-execution record of operational processes — proof that planned processes were actually carried out. Distinct from the 6.1.1 action register (which tracks ISMS-level planning actions): this tracks per-process execution evidence. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:8.1:operational_execution_register -->
<!-- column: item:8.1:reg_process_id -->
<!-- column: item:8.1:reg_execution_date -->
<!-- column: item:8.1:reg_owner -->
<!-- column: item:8.1:reg_criteria_met -->
<!-- column: item:8.1:reg_evidence_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.1:operational_execution_register -->
| Reg Process Id | Reg Execution Date | Reg Owner | Reg Criteria Met | Reg Evidence Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.1:operational_execution_register -->

## Column guidance — what to fill in

### Reg Process Id

<<MUST item:8.1:reg_process_id>>
_Why: Cross-leaf coherence_

> _Standard text:_ Process identifier per row (matches procedure's process catalog)

### Reg Execution Date

<<MUST item:8.1:reg_execution_date>>
_Why: Currency_

> _Standard text:_ Execution / iteration date per row

### Reg Owner

<<MUST item:8.1:reg_owner>>
_Why: Accountability_

> _Standard text:_ Process owner per row

### Reg Criteria Met

<<MUST item:8.1:reg_criteria_met>>
_Why: Clause 8.1 — implementing control_

> _Standard text:_ Criteria-met indicator per row (process ran per the established criteria)

### Reg Evidence Link

<<MUST item:8.1:reg_evidence_link>>
_Why: Clause 8.1 — documented information_

> _Standard text:_ Per-row link to documented evidence retained

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Outsourced Flag

<<SHOULD item:8.1:reg_outsourced_flag>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row flag where the process is outsourced (cross-link to A.5.19/A.5.20 supplier evidence)
