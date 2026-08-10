---
leaf_id: req:A.7.7:cd_cs_audit_register
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Clear Desk / Clear Screen Audit Register

<<DOC_CONTROL>>

> The catalogue of spot-check audits with findings. Each audit row: date, scope, findings, sanctions applied

<!-- TABLE-COLUMNS leaf:req:A.7.7:cd_cs_audit_register -->
<!-- column: item:A.7.7:reg_audit_id -->
<!-- column: item:A.7.7:reg_date -->
<!-- column: item:A.7.7:reg_scope -->
<!-- column: item:A.7.7:reg_findings -->
<!-- column: item:A.7.7:reg_remediation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of spot-check audits for clear desk and clear screen practices, including details like dates, scope, findings, and any actions taken. It's useful for tracking compliance and identifying areas for improvement.

## When to use it

Use this register whenever you conduct spot-check audits in your environment, and update it as needed whenever new audits are performed or findings arise.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each audit entry, so initial setup may take around an hour, with ongoing updates taking 10-15 minutes per new audit row.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.7:cd_cs_audit_register -->
| Reg Audit Id | Reg Date | Reg Scope | Reg Findings | Reg Remediation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.7:cd_cs_audit_register -->

## Column guidance — what to fill in

### Reg Audit Id

<<MUST item:A.7.7:reg_audit_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-audit unique identifier

<<GUIDANCE>>

### Reg Date

<<MUST item:A.7.7:reg_date>>
_Why: Operational discipline_

> _Standard text:_ Per-audit date

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.7.7:reg_scope>>
_Why: 27002:7.7 — appropriately enforced_

> _Standard text:_ Per-audit scope (which floors / areas covered)

<<GUIDANCE>>

### Reg Findings

<<MUST item:A.7.7:reg_findings>>
_Why: Operational discipline_

> _Standard text:_ Per-audit findings (count of violations, types observed)

<<GUIDANCE>>

### Reg Remediation

<<MUST item:A.7.7:reg_remediation>>
_Why: Closes the loop_

> _Standard text:_ Per-audit remediation log (awareness email sent, repeat-violator escalation)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Trend

<<SHOULD item:A.7.7:reg_trend>>
_Why: Continual improvement_

> _Standard text:_ Per-audit trend analysis (vs previous audit — improvement / worsening / steady)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
