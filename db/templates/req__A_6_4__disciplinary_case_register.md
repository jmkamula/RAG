---
leaf_id: req:A.6.4:disciplinary_case_register
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Disciplinary Case Register

<<DOC_CONTROL>>

> The operational catalogue of disciplinary cases (anonymised at the audit-trail layer to comply with privacy requirements). Each case: violation type, investigation outcome, action taken, decision authority, closure date. Drives the 'show me how the disciplinary process actually operates' audit question

<!-- TABLE-COLUMNS leaf:req:A.6.4:disciplinary_case_register -->
<!-- column: item:A.6.4:reg_case_id -->
<!-- column: item:A.6.4:reg_violation_type -->
<!-- column: item:A.6.4:reg_investigation_outcome -->
<!-- column: item:A.6.4:reg_action_taken -->
<!-- column: item:A.6.4:reg_decision_authority -->
<!-- column: item:A.6.4:reg_closure_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all disciplinary cases, showing how each was handled while protecting personal privacy. It’s useful for demonstrating your disciplinary process during audits.

## When to use it

Use this register whenever your organization manages disciplinary cases, and update it whenever a new case arises or details change. There’s no set schedule—just keep it current as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the initial register, plus 10 to 15 minutes for each new case you add in the future.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.4:disciplinary_case_register -->
| Reg Case Id | Reg Violation Type | Reg Investigation Outcome | Reg Action Taken | Reg Decision Authority | Reg Closure Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.4:disciplinary_case_register -->

## Column guidance — what to fill in

### Reg Case Id

<<MUST item:A.6.4:reg_case_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-case unique identifier (anonymised externally; internal traceability to personnel record preserved)

<<GUIDANCE>>

### Reg Violation Type

<<MUST item:A.6.4:reg_violation_type>>
_Why: 27002:6.4 — categorisation_

> _Standard text:_ Per-case violation type (matches the procedure's violation_scope categories)

<<GUIDANCE>>

### Reg Investigation Outcome

<<MUST item:A.6.4:reg_investigation_outcome>>
_Why: 27002:6.4 — investigation_

> _Standard text:_ Per-case investigation outcome (substantiated / not-substantiated / partially-substantiated)

<<GUIDANCE>>

### Reg Action Taken

<<MUST item:A.6.4:reg_action_taken>>
_Why: 27002:6.4 — actions_

> _Standard text:_ Per-case action taken (matches the action_range categories; 'no action' is a valid outcome where investigation didn't substantiate)

<<GUIDANCE>>

### Reg Decision Authority

<<MUST item:A.6.4:reg_decision_authority>>
_Why: Accountability_

> _Standard text:_ Per-case decision authority (named role)

<<GUIDANCE>>

### Reg Closure Date

<<MUST item:A.6.4:reg_closure_date>>
_Why: Operational discipline_

> _Standard text:_ Per-case closure date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Appeals Log

<<SHOULD item:A.6.4:reg_appeals_log>>
_Why: Fair process_

> _Standard text:_ Per-case appeals log (where appeal was lodged; status tracked)

<<GUIDANCE>>

### Reg Lessons Feed

<<SHOULD item:A.6.4:reg_lessons_feed>>
_Why: Continual improvement_

> _Standard text:_ Per-case lessons feed (where the violation surfaced a control gap, feeds back to relevant control owner / awareness curriculum)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
