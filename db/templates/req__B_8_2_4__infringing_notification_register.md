---
leaf_id: req:B.8.2.4:infringing_notification_register
control_ref: B.8.2.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Infringing Instruction Notification Register

<<DOC_CONTROL>>

> Per-notification row — the register of infringing-instruction notices issued. Often near-empty in practice, but every issued notice must be captured. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.2.4:infringing_notification_register -->
<!-- column: item:B.8.2.4:reg_notification_id -->
<!-- column: item:B.8.2.4:reg_customer_id -->
<!-- column: item:B.8.2.4:reg_instruction_summary -->
<!-- column: item:B.8.2.4:reg_legislation_cited -->
<!-- column: item:B.8.2.4:reg_notification_date -->
<!-- column: item:B.8.2.4:reg_customer_response -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of any notices you issue about instructions that may breach privacy requirements. It's useful for tracking compliance and demonstrating your response to potential privacy risks.

## When to use it

Use this register whenever you issue a notice about an instruction that could infringe on privacy, and review or update it at least once a year to ensure it stays current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours to set up the register for the first time, with additional time needed for each new notice you record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.4:infringing_notification_register -->
| Reg Notification Id | Reg Customer Id | Reg Instruction Summary | Reg Legislation Cited | Reg Notification Date | Reg Customer Response |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.4:infringing_notification_register -->

## Column guidance — what to fill in

### Reg Notification Id

<<MUST item:B.8.2.4:reg_notification_id>>
_Why: Traceability_

> _Standard text:_ Unique notification identifier per row

<<GUIDANCE>>

### Reg Customer Id

<<MUST item:B.8.2.4:reg_customer_id>>
_Why: Scope_

> _Standard text:_ Customer identifier per row

<<GUIDANCE>>

### Reg Instruction Summary

<<MUST item:B.8.2.4:reg_instruction_summary>>
_Why: Traceability_

> _Standard text:_ Instruction summary per row (what the customer asked for)

<<GUIDANCE>>

### Reg Legislation Cited

<<MUST item:B.8.2.4:reg_legislation_cited>>
_Why: §8.2.4 — applicable legislation_

> _Standard text:_ Legislation cited per row (which provision the instruction appears to infringe)

<<GUIDANCE>>

### Reg Notification Date

<<MUST item:B.8.2.4:reg_notification_date>>
_Why: Currency_

> _Standard text:_ Notification issued date per row

<<GUIDANCE>>

### Reg Customer Response

<<MUST item:B.8.2.4:reg_customer_response>>
_Why: Resolution audit trail_

> _Standard text:_ Customer response per row (withdrew / defended / disputed / no response)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Escalation

<<SHOULD item:B.8.2.4:reg_escalation>>
_Why: Governance_

> _Standard text:_ Escalation history per row (Legal / DPO / SA notification if unresolved)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
