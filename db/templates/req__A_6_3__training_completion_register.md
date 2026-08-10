---
leaf_id: req:A.6.3:training_completion_register
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Training Completion Register

<<DOC_CONTROL>>

> The operational catalogue of who has completed which training, when. Each row: personnel identifier, training module, completion date, quiz score (where applicable), next-due date. Drives the audit-defensibility 'show me every active employee completed mandatory training this year' query

<!-- TABLE-COLUMNS leaf:req:A.6.3:training_completion_register -->
<!-- column: item:A.6.3:reg_personnel_id -->
<!-- column: item:A.6.3:reg_module_id -->
<!-- column: item:A.6.3:reg_completion_date -->
<!-- column: item:A.6.3:reg_next_due -->
<!-- column: item:A.6.3:reg_status -->
<!-- column: item:A.6.3:reg_score -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of which employees have completed required training, including dates and scores. It's useful for quickly answering audit questions about staff training compliance.

## When to use it

Use this register whenever you need to track training completion for your team, and update it whenever someone finishes a training module or when new training is assigned.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch may take about 1-2 hours for a small team, with additional time needed as you add more employees or training records.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.3:training_completion_register -->
| Reg Personnel Id | Reg Module Id | Reg Completion Date | Reg Next Due | Reg Status | Reg Score |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.3:training_completion_register -->

## Column guidance — what to fill in

### Reg Personnel Id

<<MUST item:A.6.3:reg_personnel_id>>
_Why: Accountability_

> _Standard text:_ Per-row personnel identifier (links to identity register A.5.16)

<<GUIDANCE>>

### Reg Module Id

<<MUST item:A.6.3:reg_module_id>>
_Why: 27002:6.3 — curriculum_

> _Standard text:_ Per-row training module identifier (links to the curriculum catalogue)

<<GUIDANCE>>

### Reg Completion Date

<<MUST item:A.6.3:reg_completion_date>>
_Why: Audit defensibility_

> _Standard text:_ Per-row completion date

<<GUIDANCE>>

### Reg Next Due

<<MUST item:A.6.3:reg_next_due>>
_Why: 27002:6.3 — regular updates_

> _Standard text:_ Per-row next-due date (drives reminder/escalation workflow)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.6.3:reg_status>>
_Why: Operational discipline_

> _Standard text:_ Per-row status (current / overdue / waived-with-reason / N/A — for role change exemptions)

<<GUIDANCE>>

### Reg Score

<<MUST item:A.6.3:reg_score>>
_Why: 27002:6.3 — effectiveness_

> _Standard text:_ Per-row score where the module includes assessment (drives effectiveness metrics)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Phishing Sim Log

<<SHOULD item:A.6.3:reg_phishing_sim_log>>
_Why: Continuous improvement_

> _Standard text:_ Per-row phishing simulation participation log (separate from formal training — drives awareness metrics)

<<GUIDANCE>>

### Reg Overdue Alerts

<<SHOULD item:A.6.3:reg_overdue_alerts>>
_Why: Operational discipline_

> _Standard text:_ Overdue-status alerting (notification to line manager when training crosses next-due date)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
