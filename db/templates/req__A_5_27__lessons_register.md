---
leaf_id: req:A.5.27:lessons_register
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Lessons Learned Register

> A.5.27 requires lessons to be captured and acted on — without a register the action items disappear into someone's mailbox. The register tracks per-lesson: the source incident, root-cause type, control or training affected, owner, status, action due date and closure date. It feeds the periodic program review and the per-lesson improvement-action records

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each lesson captured with a unique identifier

<<MUST item:A.5.27:reg_lesson_id>>
_Why: 27002:5.27 — knowledge_

<<TEXT>>

## 2. Source incident reference per row (links to A.5.26 incident register)

<<MUST item:A.5.27:reg_source_incident>>
_Why: 27002:5.27 — from incidents_

<<TEXT>>

## 3. Root-cause type per row (drives recurring-pattern analysis)

<<MUST item:A.5.27:reg_root_cause_type>>
_Why: 27002:5.27f_

<<TEXT>>

## 4. Target per row (which control / training / procedure is affected)

<<MUST item:A.5.27:reg_target>>
_Why: 27002:5.27a_

<<TEXT>>

## 5. Named owner accountable for the action per row

<<MUST item:A.5.27:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 6. Status per row (open / in-progress / closed / accepted)

<<MUST item:A.5.27:reg_status>>
_Why: 27002:5.27a — tracking_

<<TEXT>>

## 7. Action due date + closure date per row

<<MUST item:A.5.27:reg_due_closed>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Pattern link per row where the lesson is part of a recurring cluster

<<SHOULD item:A.5.27:reg_pattern_link>>
_Why: 27002:5.27e_

<<TEXT>>

### 2. Risk register update reference per row where applicable

<<SHOULD item:A.5.27:reg_risk_update_ref>>
_Why: 27002:5.27b_

<<TEXT>>
