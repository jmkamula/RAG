---
leaf_id: req:8.3:treatment_execution_procedure
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Treatment Execution Procedure

<<DOC_CONTROL>>

> The procedure governing how treatments move from 6.1.3 plan items to implemented controls — assignment rules, status reporting cadence, escalation when items slip, residual-risk re-acceptance when treatment falls short of plan

## What this template gives you

This template helps you document how your organization moves from planned treatments to actual controls, including who is responsible, how progress is tracked, and what to do if things fall behind schedule.

## When to use it

Use this procedure whenever you need to show how treatment plans are executed and monitored in your environment. Review and update it as needed to keep it accurate and effective.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this template from scratch, as each required section will take around 10-15 minutes to write thoughtfully.

## 1. Assignment rules (how each plan item lands with an operational owner)

<<MUST item:8.3:proc_assignment>>
_Why: Clause 8.3 — implement_

<<GUIDANCE>>

<<TEXT>>

## 2. Status-reporting cadence (typically monthly for active items)

<<MUST item:8.3:proc_status_cadence>>
_Why: Operational discipline_

<<GUIDANCE>>

<<TEXT>>

## 3. Escalation rule when items slip past target date

<<MUST item:8.3:proc_escalation>>
_Why: Effectiveness_

<<GUIDANCE>>

<<TEXT>>

## 4. Residual-risk re-acceptance pathway when actual residual diverges from planned residual (back to risk owner per 6.1.3 f))

<<MUST item:8.3:proc_residual_revisit>>
_Why: Clause 8.3 — results_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner of the procedure (Risk Manager + ops lead)

<<SHOULD item:8.3:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
