---
leaf_id: req:A.5.27:lessons_register
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Lessons Learned Register

<<DOC_CONTROL>>

> A.5.27 requires lessons to be captured and acted on — without a register the action items disappear into someone's mailbox. The register tracks per-lesson: the source incident, root-cause type, control or training affected, owner, status, action due date and closure date. It feeds the periodic program review and the per-lesson improvement-action records

<!-- TABLE-COLUMNS leaf:req:A.5.27:lessons_register -->
<!-- column: item:A.5.27:reg_lesson_id -->
<!-- column: item:A.5.27:reg_source_incident -->
<!-- column: item:A.5.27:reg_root_cause_type -->
<!-- column: item:A.5.27:reg_target -->
<!-- column: item:A.5.27:reg_owner -->
<!-- column: item:A.5.27:reg_status -->
<!-- column: item:A.5.27:reg_due_closed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically capture and track lessons learned from incidents, ensuring that action items are followed up and improvements are documented for future reference.

## When to use it

Use this register whenever lessons are identified in your environment, such as after incidents or reviews, and update it as needed to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours setting up the initial register, with additional time required for each new lesson or incident you document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.27:lessons_register -->
| Reg Lesson Id | Reg Source Incident | Reg Root Cause Type | Reg Target | Reg Owner | Reg Status | Reg Due Closed |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.27:lessons_register -->

## Column guidance — what to fill in

### Reg Lesson Id

<<MUST item:A.5.27:reg_lesson_id>>
_Why: 27002:5.27 — knowledge_

> _Standard text:_ Each lesson captured with a unique identifier

<<GUIDANCE>>

### Reg Source Incident

<<MUST item:A.5.27:reg_source_incident>>
_Why: 27002:5.27 — from incidents_

> _Standard text:_ Source incident reference per row (links to A.5.26 incident register)

<<GUIDANCE>>

### Reg Root Cause Type

<<MUST item:A.5.27:reg_root_cause_type>>
_Why: 27002:5.27f_

> _Standard text:_ Root-cause type per row (drives recurring-pattern analysis)

<<GUIDANCE>>

### Reg Target

<<MUST item:A.5.27:reg_target>>
_Why: 27002:5.27a_

> _Standard text:_ Target per row (which control / training / procedure is affected)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.27:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named owner accountable for the action per row

<<GUIDANCE>>

### Reg Status

<<MUST item:A.5.27:reg_status>>
_Why: 27002:5.27a — tracking_

> _Standard text:_ Status per row (open / in-progress / closed / accepted)

<<GUIDANCE>>

### Reg Due Closed

<<MUST item:A.5.27:reg_due_closed>>
_Why: Operational discipline_

> _Standard text:_ Action due date + closure date per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Pattern Link

<<SHOULD item:A.5.27:reg_pattern_link>>
_Why: 27002:5.27e_

> _Standard text:_ Pattern link per row where the lesson is part of a recurring cluster

<<GUIDANCE>>

### Reg Risk Update Ref

<<SHOULD item:A.5.27:reg_risk_update_ref>>
_Why: 27002:5.27b_

> _Standard text:_ Risk register update reference per row where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
